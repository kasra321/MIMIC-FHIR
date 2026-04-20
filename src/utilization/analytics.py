

from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import seaborn as sns

SOURCE_PALETTE = {"mimic-iv": "#2c7bb6", "synthea": "#d7191c"}

def _source_colors(sources: pd.Series) -> list[str]:
    return [SOURCE_PALETTE.get(s, "#999999") for s in sources]


def source_comparison_table(stats_df: pd.DataFrame) -> pd.DataFrame:
    """Pivot /utilization/stats response into a MIMIC-vs-Synthea comparison."""
    agg = (
        stats_df.groupby("source")
        .agg(
            encounters=("total_encounters", "sum"),
            avg_los_hrs=("avg_los_hours", "mean"),
            avg_age=("avg_age", "mean"),
            avg_enc_12m=("avg_encounters_12m", "mean"),
            avg_chronic=("avg_chronic_conditions", "mean"),
        )
        .round(1)
    )
    return agg

def plot_encounter_class_breakdown(stats_df: pd.DataFrame) -> plt.Figure:
    """Grouped bar chart of encounter counts by class, coloured by source."""
    fig, ax = plt.subplots(figsize=(10, 5))
    pivot = stats_df.pivot_table(
        index="encounter_class", columns="source",
        values="total_encounters", fill_value=0,
    )
    pivot.plot.bar(ax=ax, color=[SOURCE_PALETTE.get(c, "#999") for c in pivot.columns])
    ax.set_ylabel("Encounters")
    ax.set_title("Encounter Volume by Class and Source")
    ax.set_xlabel("")
    ax.ticklabel_format(axis="y", style="plain")
    plt.xticks(rotation=0)
    plt.tight_layout()
    return fig

def plot_los_distribution(df: pd.DataFrame, cap_hours: float = 200) -> plt.Figure:
    """Histogram of length-of-stay (hours), split by source."""
    fig, ax = plt.subplots(figsize=(10, 5))
    for source, grp in df.groupby("source"):
        vals = grp["los_hours"].dropna().clip(upper=cap_hours)
        ax.hist(vals, bins=60, alpha=0.6, label=source,
                color=SOURCE_PALETTE.get(source, "#999"))
    ax.set_xlabel("Length of Stay (hours)")
    ax.set_ylabel("Encounters")
    ax.set_title(f"LOS Distribution (capped at {cap_hours}h)")
    ax.legend()
    plt.tight_layout()
    return fig

def plot_demographic_summary(df: pd.DataFrame) -> plt.Figure:
    """2x1 grid: age histogram and gender split by source."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Age
    ax = axes[0]
    for source, grp in df.groupby("source"):
        vals = grp["age_at_visit"].dropna()
        ax.hist(vals, bins=40, alpha=0.6, label=source,
                color=SOURCE_PALETTE.get(source, "#999"))
    ax.set_xlabel("Age at Visit")
    ax.set_ylabel("Encounters")
    ax.set_title("Age Distribution")
    ax.legend()

    # Gender
    ax = axes[1]
    ct = df.groupby(["source", "gender"]).size().unstack(fill_value=0)
    ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100
    ct_pct.plot.bar(ax=ax, stacked=True, colormap="Set2")
    ax.set_ylabel("Percent")
    ax.set_title("Gender Split by Source")
    ax.set_xlabel("")
    plt.xticks(rotation=0)

    plt.tight_layout()
    return fig


def plot_utilization_heatmap(df: pd.DataFrame) -> plt.Figure:
    """Heatmap of mean prior-utilization metrics, grouped by source."""
    metrics = [
        "encounters_6m", "encounters_12m", "encounters_24m",
        "ed_visits_12m", "inpatient_12m", "ambulatory_12m", "wellness_12m",
    ]
    agg = df.groupby("source")[metrics].mean()
    fig, ax = plt.subplots(figsize=(10, 3))
    sns.heatmap(agg, annot=True, fmt=".2f", cmap="YlOrRd", ax=ax)
    ax.set_title("Mean Prior-Utilization Metrics by Source")
    ax.set_ylabel("")
    plt.tight_layout()
    return fig

def plot_condition_burden(df: pd.DataFrame) -> plt.Figure:
    """Scatter: chronic conditions vs 12-month encounter frequency."""
    fig, ax = plt.subplots(figsize=(8, 6))
    for source, grp in df.groupby("source"):
        ax.scatter(
            grp["chronic_conditions"], grp["encounters_12m"],
            alpha=0.3, s=10, label=source,
            color=SOURCE_PALETTE.get(source, "#999"),
        )
    ax.set_xlabel("Chronic Conditions")
    ax.set_ylabel("Encounters in Prior 12 Months")
    ax.set_title("Condition Burden vs. Utilization Frequency")
    ax.legend()
    plt.tight_layout()
    return fig


def plot_patient_timeline(encounters_df: pd.DataFrame) -> plt.Figure:
    """Gantt-style timeline for a single patient's encounters."""
    df = encounters_df.copy()
    df["period_start"] = pd.to_datetime(df["period_start"])
    df["period_end"] = pd.to_datetime(df["period_end"])
    df = df.sort_values("period_start")

    class_colors = {
        "EMER": "#e41a1c", "OBSENC": "#377eb8", "ACUTE": "#ff7f00",
        "AMB": "#4daf4a", "SS": "#984ea3", "IMP": "#377eb8",
        "HH": "#a65628", "VR": "#f781bf",
    }

    fig, ax = plt.subplots(figsize=(12, max(3, len(df) * 0.5 + 1)))
    for i, (_, row) in enumerate(df.iterrows()):
        start = row["period_start"]
        end = row["period_end"]
        color = class_colors.get(row.get("encounter_class"), "#999999")
        ax.barh(i, (end - start).total_seconds() / 3600,
                left=mdates.date2num(start), height=0.6, color=color,
                edgecolor="white", linewidth=0.5)
        label = row.get("encounter_class", "")
        los = row.get("los_hours")
        if los is not None:
            label += f"  ({los:.0f}h)"
        ax.text(mdates.date2num(end), i, f"  {label}", va="center", fontsize=9)

    ax.set_yticks(range(len(df)))
    ax.set_yticklabels([f"Enc {i+1}" for i in range(len(df))])
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()
    ax.set_title("Patient Encounter Timeline")
    ax.invert_yaxis()
    plt.tight_layout()
    return fig
