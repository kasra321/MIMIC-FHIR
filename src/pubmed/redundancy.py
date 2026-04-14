"""
PubMed Bucket-Based Redundancy Analysis
========================================
Extract, normalize, and analyze redundancy in MIMIC-IV PubMed
abstracts using Gemini for metadata extraction and bucketing.
"""
import json, re, time
from pathlib import Path
from collections import Counter

import pandas as pd

BASE = Path(__file__).resolve().parent.parent.parent
LOCAL = BASE / "local"
ABSTRACTS_PATH = LOCAL / "pubmed_abstracts_2025.txt"
CHECKPOINT_PATH = LOCAL / "pubmed_extracted.json"
FINAL_PATH = LOCAL / "pubmed_extracted_final.json"
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

NORMALIZE_PROMPT = """I have three lists of free-text field values extracted from {n} research papers.
Many values are near-duplicates or minor variations of the same concept.

Your task: for each list, cluster the unique values into a reasonable number of
canonical buckets based on semantic similarity and frequency. Then return a mapping
from every original value to its bucket.

Guidelines:
- Aim for 8-15 buckets per field — enough to be meaningful, few enough to show patterns
- Group by semantic similarity (e.g., "XGBoost", "random forest", "gradient boosting", "LightGBM" are all tree-based ensemble methods)
- If a value doesn't fit any natural cluster, use an "Other" bucket
- Bucket names should be concise and descriptive

For example, methodologies like "Cox regression" and "Kaplan-Meier survival analysis"
might cluster into a "Survival Analysis" bucket; diseases like "sepsis", "severe sepsis",
and "septic shock" might cluster into "Sepsis/Septic Shock". These are just illustrations —
let the actual data guide your groupings.

Return a JSON object with three keys:
"methodology_map", "outcome_map", "disease_map"
Each is an object mapping every original value to its canonical bucket name.

Return ONLY valid JSON. No markdown fences, no explanation.

UNIQUE METHODOLOGIES ({nm} values):
{methods}

UNIQUE OUTCOMES ({no} values):
{outcomes}

UNIQUE DISEASES ({nd} values):
{diseases}
"""


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


def extract_all(client, batches, checkpoint_path=CHECKPOINT_PATH):
    """Run Gemini extraction over all batches with crash-safe checkpointing."""
    try:
        with open(checkpoint_path) as f:
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
            with open(checkpoint_path, "w") as f:
                json.dump(all_extracted, f)
            print(f"  Batch {i+1}/{len(batches)}: +{len(parsed)} (total: {len(all_extracted)})")
        except Exception as e:
            print(f"  Batch {i+1} failed ({e}), retrying halves...")
            mid = len(batch) // 2
            for label, half in [("a", batch[:mid]), ("b", batch[mid:])]:
                try:
                    parsed = _call(half)
                    all_extracted.extend(parsed)
                    with open(checkpoint_path, "w") as f:
                        json.dump(all_extracted, f)
                    print(f"    Half {label}: +{len(parsed)} (total: {len(all_extracted)})")
                except Exception as e2:
                    print(f"    Half {label} FAILED: {e2}")
        time.sleep(2)

    print(f"[EXTRACT] Done: {len(all_extracted)} articles")
    return all_extracted


def normalize(client, all_extracted):
    """Gemini-based normalization of free-text fields into canonical buckets."""
    df = pd.DataFrame(all_extracted)
    unique_methods = df["methodology"].unique().tolist()
    unique_outcomes = df["outcome_metric"].unique().tolist()
    unique_diseases = df["disease_area"].unique().tolist()
    print(f"[NORMALIZE] {len(df)} articles — {len(unique_methods)} methods, "
          f"{len(unique_outcomes)} outcomes, {len(unique_diseases)} diseases")

    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=NORMALIZE_PROMPT.format(
            n=len(df),
            nm=len(unique_methods), methods=json.dumps(unique_methods),
            no=len(unique_outcomes), outcomes=json.dumps(unique_outcomes),
            nd=len(unique_diseases), diseases=json.dumps(unique_diseases),
        ),
    )
    maps = json.loads(_clean_json_response(resp.text))

    df["method_bucket"] = df["methodology"].map(maps["methodology_map"]).fillna("Other")
    df["outcome_bucket"] = df["outcome_metric"].map(maps["outcome_map"]).fillna("Other")
    df["disease_bucket"] = df["disease_area"].map(maps["disease_map"]).fillna("Other")

    print(f"[NORMALIZE] Buckets: {df['method_bucket'].nunique()} methods, "
          f"{df['outcome_bucket'].nunique()} outcomes, {df['disease_bucket'].nunique()} diseases")
    return df


def redundancy_analysis(df):
    """Print full redundancy report from a normalized DataFrame."""
    total = len(df)
    print(f"{'='*60}")
    print(f"MIMIC-IV PubMed Redundancy Analysis — {total} articles")
    print(f"{'='*60}\n")

    # 1. Utilization-focused
    util_outcomes = ["Mortality (in-hospital)", "Mortality (30-day)",
                     "Mortality (long-term)", "Length of Stay", "Readmission"]
    df["is_utilization"] = df["outcome_bucket"].isin(util_outcomes)
    util_count = df["is_utilization"].sum()
    print(f"1. UTILIZATION-FOCUSED STUDIES: {util_count}/{total} ({100*util_count/total:.1f}%)")
    for outcome in util_outcomes:
        n = (df["outcome_bucket"] == outcome).sum()
        if n > 0:
            print(f"     {outcome}: {n} ({100*n/total:.1f}%)")

    # 2. Data transform overlap
    print(f"\n2. DATA TRANSFORM OVERLAP:")
    all_transforms = [t for transforms in df["data_transforms"] for t in transforms]
    for t, c in Counter(all_transforms).most_common():
        print(f"     {t}: {c} studies ({100*c/total:.1f}%)")
    df["n_transforms"] = df["data_transforms"].apply(len)
    shared = (df["n_transforms"] >= 3).sum()
    print(f"\n   3+ transforms: {shared}/{total} ({100*shared/total:.1f}%)")

    # 3. Disease distribution
    print(f"\n3. TOP DISEASE AREAS:")
    for disease, count in df["disease_bucket"].value_counts().head(10).items():
        print(f"     {disease}: {count} ({100*count/total:.1f}%)")

    # 4. Methodology distribution
    print(f"\n4. METHODOLOGY DISTRIBUTION:")
    for method, count in df["method_bucket"].value_counts().items():
        print(f"     {method}: {count} ({100*count/total:.1f}%)")

    # 5. Redundancy clusters
    print(f"\n5. REDUNDANCY CLUSTERS (disease × outcome × method):")
    clusters = df.groupby(["disease_bucket", "outcome_bucket", "method_bucket"]).size()
    clusters = clusters.sort_values(ascending=False)
    redundant = clusters[clusters > 1].sum()
    print(f"   Redundant (2+ identical): {redundant}/{total} ({100*redundant/total:.1f}%)")
    print(f"\n   Top 10:")
    for (disease, outcome, method), count in clusters.head(10).items():
        print(f"     [{count}] {disease} × {outcome} × {method}")

    # 6. Effort estimate
    weeks = redundant * 2
    print(f"\n6. REDUNDANT EFFORT: {redundant} studies × 2 wk = "
          f"{weeks} person-weeks = {weeks/52:.1f} person-years")
