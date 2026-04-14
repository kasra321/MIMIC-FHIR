"""
PubMed Semantic Clustering
==========================
Embed MIMIC-IV PubMed article metadata and cluster via
hierarchical agglomeration to surface natural topic groupings.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sentence_transformers import SentenceTransformer
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import cosine_similarity

BASE = Path(__file__).resolve().parent.parent.parent
LOCAL = BASE / "local"
DATA_PATH = LOCAL / "pubmed_extracted_final.json"
EMBED_CACHE = LOCAL / "pubmed_embeddings.npy"
MODEL_NAME = "all-MiniLM-L6-v2"


def load_articles(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load extracted PubMed JSON → DataFrame with composite text column."""
    print(f"[LOAD] Reading {path}")
    with open(path) as f:
        articles = json.load(f)
    df = pd.DataFrame(articles)
    df["text"] = (
        df["data_transforms"].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
        + " | " + df["outcome_metric"].fillna("")
        + " | " + df["disease_area"].fillna("")
    )
    print(f"[LOAD] {len(df)} articles loaded")
    return df


def embed(
    df: pd.DataFrame,
    text_col: str = "text",
    cache_path: Path = EMBED_CACHE,
    model_name: str = MODEL_NAME,
) -> np.ndarray:
    """N x D embeddings with disk cache. Recomputes if row count changes."""
    if cache_path.exists():
        cached = np.load(cache_path)
        if len(cached) == len(df):
            print(f"[EMBED] Cache hit: {cache_path} ({cached.shape})")
            return cached
        print(f"[EMBED] Cache stale ({len(cached)} != {len(df)}), recomputing")
    model = SentenceTransformer(model_name)
    emb = model.encode(
        df[text_col].tolist(),
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,
    )
    np.save(cache_path, emb)
    print(f"[EMBED] Saved {emb.shape} to {cache_path}")
    return emb


def cluster(
    embeddings: np.ndarray,
    n_clusters: int = 10,
    method: str = "ward",
) -> tuple[np.ndarray, np.ndarray]:
    """Hierarchical clustering → (labels, linkage_matrix)."""
    Z = linkage(embeddings, method=method)
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
