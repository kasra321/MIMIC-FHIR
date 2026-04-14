"""
PubMed Redundancy Analysis
===========================
Fetch, extract, embed, and cluster MIMIC-IV PubMed article metadata
to quantify research redundancy via hierarchical agglomeration.

Per-field embeddings (data_transforms, outcome_metric, disease_area)
enable independent and combined clustering with dynamic k selection.
"""
import json, re, time
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sentence_transformers import SentenceTransformer
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity

BASE = Path(__file__).resolve().parent.parent.parent
LOCAL = BASE / "local"
ABSTRACTS_PATH = LOCAL / "pubmed_abstracts_2025.txt"
DATA_PATH = LOCAL / "pubmed_extracted_final.json"
EMBED_CACHE = LOCAL / "pubmed_embeddings.npz"
MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 50

EXTRACT_PROMPT = """For each abstract below, extract a JSON object with these fields:
- pmid: the PubMed ID
- primary_question: the core research question in one sentence
- methodology: statistical/ML methods used (e.g., "logistic regression, LASSO, XGBoost")
- primary_conclusion: the main finding in one sentence
- data_transforms: list from ["ICD-code cohort selection", "vital sign extraction", "lab value aggregation", "mortality labeling", "LOS calculation", "medication extraction", "demographic filtering", "time-series windowing"]
- outcome_metric: primary outcome (e.g., "30-day mortality", "LOS", "readmission")
- disease_area: primary disease/condition studied

Return ONLY a valid JSON array. No markdown fences, no explanation, no extra text.

ABSTRACTS:
{batch_text}
"""

FIELDS = ["transforms", "outcomes", "diseases"]


# ---------------------------------------------------------------------------
# Gemini extraction helpers (for reproducibility — not called in normal flow)
# ---------------------------------------------------------------------------

def _clean_json_response(text):
    """Strip markdown fences, thinking tags, and other wrappers."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"^```(?:json)?\s*\n?", "", text.strip())
    text = re.sub(r"\n?```\s*$", "", text.strip())
    return text.strip()


def fetch_abstracts(query='"MIMIC-IV"', since="2025", retmax=2000, rate_limit=0.35):
    """Fetch abstracts from PubMed and return concatenated text."""
    from metapub import PubMedFetcher

    fetch = PubMedFetcher()
    pmids = fetch.pmids_for_query(query, since=since, retmax=retmax)
    print(f"Found {len(pmids)} articles")

    all_abstracts = ""
    skipped = 0
    for i, pmid in enumerate(pmids):
        try:
            art = fetch.article_by_pmid(pmid)
            if art.abstract:
                all_abstracts += f"PMID: {pmid}\nTITLE: {art.title}\nABSTRACT: {art.abstract}\n\n---\n\n"
        except Exception:
            skipped += 1
        if (i + 1) % 100 == 0:
            print(f"  Fetched {i + 1}/{len(pmids)}")
        time.sleep(rate_limit)

    print(f"Collected {len(pmids) - skipped} abstracts ({skipped} skipped)")
    return all_abstracts


def load_abstracts(path=ABSTRACTS_PATH, batch_size=BATCH_SIZE):
    """Load raw abstracts file → list of batches."""
    with open(path) as f:
        all_abstracts = f.read()
    abstracts = [a.strip() for a in all_abstracts.split("---") if a.strip()]
    batches = [abstracts[i:i+batch_size] for i in range(0, len(abstracts), batch_size)]
    print(f"[LOAD] {len(abstracts)} abstracts in {len(batches)} batches")
    return abstracts, batches


def extract_all(client, batches, output_path=DATA_PATH):
    """Run Gemini extraction over all batches with crash-safe checkpointing."""
    try:
        with open(output_path) as f:
            all_extracted = json.load(f)
        start = len(all_extracted) // BATCH_SIZE
        print(f"[EXTRACT] Resuming from batch {start} ({len(all_extracted)} done)")
    except (FileNotFoundError, json.JSONDecodeError):
        all_extracted = []
        start = 0

    def _call(texts):
        batch_text = "\n\n".join(texts)
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=EXTRACT_PROMPT.format(batch_text=batch_text),
        )
        return json.loads(_clean_json_response(resp.text))

    for i, batch in enumerate(batches[start:], start=start):
        try:
            parsed = _call(batch)
            all_extracted.extend(parsed)
            with open(output_path, "w") as f:
                json.dump(all_extracted, f)
            print(f"  Batch {i+1}/{len(batches)}: +{len(parsed)} (total: {len(all_extracted)})")
        except Exception as e:
            print(f"  Batch {i+1} failed ({e}), retrying halves...")
            mid = len(batch) // 2
            for label, half in [("a", batch[:mid]), ("b", batch[mid:])]:
                try:
                    parsed = _call(half)
                    all_extracted.extend(parsed)
                    with open(output_path, "w") as f:
                        json.dump(all_extracted, f)
                    print(f"    Half {label}: +{len(parsed)} (total: {len(all_extracted)})")
                except Exception as e2:
                    print(f"    Half {label} FAILED: {e2}")
        time.sleep(2)

    print(f"[EXTRACT] Done: {len(all_extracted)} articles")
    return all_extracted


# ---------------------------------------------------------------------------
# Core pipeline: load → embed → cluster → visualize
# ---------------------------------------------------------------------------

def load_articles(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load extracted PubMed JSON → DataFrame."""
    print(f"[LOAD] Reading {path}")
    with open(path) as f:
        articles = json.load(f)
    df = pd.DataFrame(articles)
    print(f"[LOAD] {len(df)} articles loaded")
    return df


def embed(
    df: pd.DataFrame,
    cache_path: Path = EMBED_CACHE,
    model_name: str = MODEL_NAME,
) -> dict[str, np.ndarray]:
    """Per-field embeddings with disk cache.

    Returns dict with keys: "transforms", "outcomes", "diseases", "combined".
    Each value is an (N, D) or (N, 3*D) array.
    """
    if cache_path.exists():
        cached = dict(np.load(cache_path))
        if len(cached.get("transforms", [])) == len(df):
            print(f"[EMBED] Cache hit: {cache_path}")
            for k in FIELDS:
                print(f"  {k}: {cached[k].shape}")
            print(f"  combined: {cached['combined'].shape}")
            return cached
        print(f"[EMBED] Cache stale, recomputing")

    model = SentenceTransformer(model_name)

    texts = {
        "transforms": df["data_transforms"].apply(
            lambda x: ", ".join(x) if isinstance(x, list) else str(x)
        ).tolist(),
        "outcomes": df["outcome_metric"].fillna("").tolist(),
        "diseases": df["disease_area"].fillna("").tolist(),
    }

    result = {}
    for field, sentences in texts.items():
        emb = model.encode(
            sentences, batch_size=64,
            show_progress_bar=True, normalize_embeddings=True,
        )
        result[field] = emb
        print(f"[EMBED] {field}: {emb.shape}")

    result["combined"] = np.hstack([result[f] for f in FIELDS])
    print(f"[EMBED] combined: {result['combined'].shape}")

    np.savez(cache_path, **result)
    print(f"[EMBED] Saved to {cache_path}")
    return result


def optimal_k(embeddings: np.ndarray, k_range=range(3, 16), method="ward"):
    """Find best k via silhouette score. Returns (best_k, scores_dict)."""
    Z = linkage(embeddings, method=method)
    scores = {}
    for k in k_range:
        labels = fcluster(Z, t=k, criterion="maxclust")
        scores[k] = silhouette_score(embeddings, labels, metric="euclidean")

    best_k = max(scores, key=scores.get)
    print(f"[OPTIMAL_K] Best k={best_k} (silhouette={scores[best_k]:.3f})")

    plt.figure(figsize=(8, 4))
    plt.plot(list(scores.keys()), list(scores.values()), "o-")
    plt.axvline(best_k, color="red", linestyle="--", alpha=0.7, label=f"best k={best_k}")
    plt.xlabel("Number of clusters (k)")
    plt.ylabel("Silhouette score")
    plt.title("Silhouette Score vs k")
    plt.legend()
    plt.tight_layout()
    plt.show()

    return best_k


def cluster(
    embeddings: np.ndarray,
    n_clusters: int | None = None,
    method: str = "ward",
) -> tuple[np.ndarray, np.ndarray]:
    """Hierarchical clustering → (labels, linkage_matrix).

    If n_clusters is None, uses optimal_k() to find it automatically.
    """
    Z = linkage(embeddings, method=method)
    if n_clusters is None:
        n_clusters = optimal_k(embeddings, method=method)
    labels = fcluster(Z, t=n_clusters, criterion="maxclust")
    print(f"[CLUSTER] {len(set(labels))} clusters from {len(embeddings)} articles")
    return labels, Z


def plot_dendrogram(Z, p=30):
    """Truncated dendrogram of the linkage matrix."""
    plt.figure(figsize=(14, 5))
    dendrogram(Z, truncate_mode="lastp", p=p, leaf_rotation=90)
    plt.title("Hierarchical Clustering Dendrogram (top 30 nodes)")
    plt.xlabel("Cluster size")
    plt.ylabel("Distance")
    plt.tight_layout()
    plt.show()


def plot_tsne(emb, labels):
    """2D t-SNE scatter colored by cluster label."""
    coords = TSNE(n_components=2, metric="cosine", random_state=42, perplexity=30).fit_transform(emb)
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(coords[:, 0], coords[:, 1], c=labels, cmap="tab10", s=8, alpha=0.7)
    plt.colorbar(scatter, label="Cluster")
    plt.title("t-SNE of PubMed Article Embeddings (colored by cluster)")
    plt.tight_layout()
    plt.show()


def plot_similarity_heatmap(emb, labels):
    """Cosine similarity heatmap of cluster centroids."""
    cluster_ids = sorted(set(labels))
    centroids = np.array([emb[labels == c].mean(axis=0) for c in cluster_ids])
    sim = cosine_similarity(centroids)
    plt.figure(figsize=(8, 6))
    sns.heatmap(sim, annot=True, fmt=".2f", cmap="YlOrRd",
                xticklabels=cluster_ids, yticklabels=cluster_ids)
    plt.title("Cosine Similarity Between Cluster Centroids")
    plt.tight_layout()
    plt.show()


def summary_table(df, labels) -> pd.DataFrame:
    """Per-cluster summary: count + top diseases, outcomes, methods."""
    df = df.copy()
    df["cluster"] = labels
    rows = []
    for c in sorted(set(labels)):
        sub = df[df["cluster"] == c]
        top = lambda col, n=5: ", ".join(sub[col].value_counts().head(n).index.tolist())
        rows.append({
            "cluster": c,
            "n": len(sub),
            "top_diseases": top("disease_area"),
            "top_outcomes": top("outcome_metric"),
            "top_methods": top("methodology"),
        })
    return pd.DataFrame(rows).sort_values("n", ascending=False)
