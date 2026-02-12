"""Constants, processing, plotting, and stats helpers for vital signs EDA."""

from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import Patch
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform
from scipy.stats import chi2_contingency, ks_2samp, ttest_ind

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VITALS_6 = {
    "8310-5": "body_temperature",
    "8867-4": "heart_rate",
    "9279-1": "respiratory_rate",
    "2708-6": "oxygen_saturation",
    "8480-6": "systolic_bp",
    "8462-4": "diastolic_bp",
}

VITALS_5 = {   
    "8867-4": "heart_rate",
    "9279-1": "respiratory_rate",
    "2708-6": "oxygen_saturation",
    "8480-6": "systolic_bp",
    "8462-4": "diastolic_bp",
}


VITALS_3 = {
    "8867-4": "heart_rate",
    "8480-6": "systolic_bp",
    "8462-4": "diastolic_bp",
}

DISPLAY_NAMES = {
    "body_temperature": "Temp",
    "heart_rate": "HR",
    "respiratory_rate": "RR",
    "oxygen_saturation": "SpO2",
    "systolic_bp": "SBP",
    "diastolic_bp": "DBP",
}

MISS_COLS = ["temp", "hr", "rr", "spo2", "sbp", "dbp"]

PROJECT_ROOT = Path(__file__).parent.parent.parent
SILVER_PATH = PROJECT_ROOT / "output" / "silver" / "silver_vitals.parquet"

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------


def connect_vitals(path: Path | None = None) -> duckdb.DuckDBPyConnection:
    """Return an in-memory DuckDB connection with a ``vitals`` view."""
    path = path or SILVER_PATH
    conn = duckdb.connect(":memory:")
    conn.execute(
        f"CREATE VIEW vitals AS SELECT * FROM read_parquet('{path}')"
    )
    return conn


# ---------------------------------------------------------------------------
# Processing helpers
# ---------------------------------------------------------------------------


def compute_co_occurrence(miss_df: pd.DataFrame) -> pd.DataFrame:
    """P(col present | row present) matrix from missingness indicators.

    Parameters
    ----------
    miss_df : DataFrame with columns ``{vital}_present`` (0/1).

    Returns
    -------
    DataFrame indexed and columned by vital short names.
    """
    vitals = MISS_COLS
    cols = [f"{v}_present" for v in vitals]
    co_occur = pd.DataFrame(index=vitals, columns=vitals, dtype=float)
    for v1 in vitals:
        for v2 in vitals:
            mask = miss_df[f"{v1}_present"] == 1
            if mask.sum() > 0:
                co_occur.loc[v1, v2] = round(
                    100.0 * miss_df.loc[mask, f"{v2}_present"].mean(), 1
                )
            else:
                co_occur.loc[v1, v2] = 0.0
    return co_occur


def assign_duration_bucket(hrs: float) -> str:
    """Map hours to a categorical duration bucket."""
    if hrs < 1:
        return "<1 hr"
    elif hrs < 4:
        return "1-4 hrs"
    elif hrs < 12:
        return "4-12 hrs"
    elif hrs < 24:
        return "12-24 hrs"
    elif hrs < 72:
        return "1-3 days"
    else:
        return ">3 days"


def decode_missingness_pattern(pattern: str) -> str:
    """Decode a binary pattern string like '111110' -> 'Missing: DBP'."""
    labels = ["Temp", "HR", "RR", "SpO2", "SBP", "DBP"]
    missing = [v for v, c in zip(labels, pattern) if c == "0"]
    if len(missing) == 0:
        return "All present"
    elif len(missing) == 6:
        return "All missing"
    return f"Missing: {', '.join(missing)}"


def filter_complete(df: pd.DataFrame, n_col: str, required: int) -> pd.DataFrame:
    """Filter to complete timestamps and recompute deltas + positions."""
    complete = (
        df[df[n_col] == required]
        .sort_values(["encounter_id", "effective_datetime"])
        .copy()
    )
    complete["delta_min"] = (
        complete.groupby("encounter_id")["effective_datetime"]
        .diff().dt.total_seconds() / 60
    )
    complete["obs_position"] = complete.groupby("encounter_id").cumcount() + 1
    complete["total_obs_in_encounter"] = complete.groupby("encounter_id")[
        "encounter_id"
    ].transform("count")
    return complete


# ---------------------------------------------------------------------------
# Plotting helpers
# ---------------------------------------------------------------------------


def plot_completeness_bar(
    df: pd.DataFrame, ax: plt.Axes | None = None, n_vitals: int = 6
):
    """Color-coded bar chart of timestamp completeness with % labels."""
    if ax is None:
        _, ax = plt.subplots(figsize=(10, 5))

    colors = [
        "#ff6b6b" if x < n_vitals - 1
        else ("#ffd93d" if x == n_vitals - 1 else "#6bcb77")
        for x in df["num_vitals"]
    ]
    bars = ax.bar(
        df["num_vitals"].astype(str), df["pct"], color=colors, edgecolor="black"
    )
    ax.set_xlabel("Number of Vitals Recorded", fontsize=12)
    ax.set_ylabel("Percentage of Timestamps (%)", fontsize=12)
    ax.set_title(
        "Timestamp Completeness Distribution", fontsize=14, fontweight="bold"
    )
    for bar, pct in zip(bars, df["pct"]):
        ax.annotate(
            f"{pct}%",
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )
    legend_elements = [
        Patch(facecolor="#6bcb77", edgecolor="black",
              label=f"Complete ({n_vitals} vitals)"),
        Patch(facecolor="#ffd93d", edgecolor="black",
              label=f"{n_vitals - 1} of {n_vitals}"),
        Patch(facecolor="#ff6b6b", edgecolor="black",
              label=f"<{n_vitals - 1}"),
    ]
    ax.legend(handles=legend_elements, loc="upper left")
    return ax


def plot_heatmap(
    matrix: pd.DataFrame,
    title: str,
    ax: plt.Axes | None = None,
    *,
    lower_triangle: bool = True,
    fmt: str = ".2f",
    cmap: str = "RdBu_r",
    vmin: float | None = None,
    vmax: float | None = None,
):
    """Lower-triangle (or full) heatmap with annotations."""
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 6))

    mask = None
    if lower_triangle:
        mask = np.triu(np.ones_like(matrix, dtype=bool), k=1)

    sns.heatmap(
        matrix.astype(float),
        annot=True,
        fmt=fmt,
        cmap=cmap,
        center=0 if vmin is None else None,
        vmin=vmin if vmin is not None else -1,
        vmax=vmax if vmax is not None else 1,
        ax=ax,
        mask=mask,
        square=True,
    )
    ax.set_title(title, fontsize=13, fontweight="bold")
    return ax


def plot_delta_histogram(
    buckets: pd.DataFrame, title: str, ax: plt.Axes | None = None
):
    """Bars + cumulative overlay line for time-delta buckets."""
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 6))

    x = range(len(buckets))
    bars = ax.bar(
        x, buckets["pct"], color="steelblue", edgecolor="black", alpha=0.8
    )
    ax.set_xticks(list(x))
    ax.set_xticklabels(buckets["time_bucket"], fontsize=11)
    ax.set_xlabel("Time Delta Between Complete Timestamps", fontsize=12)
    ax.set_ylabel("Percentage (%)", fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")

    for bar, pct in zip(bars, buckets["pct"]):
        ax.annotate(
            f"{pct}%",
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
            ha="center",
            va="bottom",
            fontsize=10,
        )

    # Cumulative line on twin axis
    cumulative = buckets["pct"].cumsum()
    ax2 = ax.twinx()
    ax2.plot(
        list(x), cumulative, color="red", marker="o", linewidth=2, markersize=8
    )
    ax2.set_ylabel("Cumulative %", fontsize=12, color="red")
    ax2.tick_params(axis="y", labelcolor="red")
    ax2.axhline(y=80, color="green", linestyle="--", alpha=0.7, linewidth=2)
    ax2.annotate("80% threshold", xy=(len(x) - 2, 82), color="green", fontsize=10)
    return ax


def plot_temporal_panels(temporal_df: pd.DataFrame):
    """3-panel figure: hour-of-day, encounter phase, day-of-week presence rates."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Panel 1: Hour of Day
    ax1 = axes[0]
    hourly = temporal_df.groupby("hour_of_day").agg(
        temp_rate=("temp_present", "mean"),
        hr_rate=("hr_present", "mean"),
        spo2_rate=("spo2_present", "mean"),
    ).reset_index()

    ax1.plot(
        hourly["hour_of_day"], hourly["temp_rate"] * 100,
        "o-", color="red", linewidth=2, markersize=6, label="Temperature",
    )
    ax1.plot(
        hourly["hour_of_day"], hourly["hr_rate"] * 100,
        "s--", color="blue", linewidth=1.5, markersize=4, alpha=0.7, label="Heart Rate",
    )
    ax1.plot(
        hourly["hour_of_day"], hourly["spo2_rate"] * 100,
        "^--", color="green", linewidth=1.5, markersize=4, alpha=0.7, label="SpO2",
    )
    ax1.set_xlabel("Hour of Day", fontsize=11)
    ax1.set_ylabel("Presence Rate (%)", fontsize=11)
    ax1.set_title("Vital Presence by Hour of Day", fontsize=12, fontweight="bold")
    ax1.legend(loc="lower right", fontsize=9)
    ax1.set_xticks([0, 6, 12, 18, 23])
    ax1.grid(True, alpha=0.3)
    ax1.axvspan(22, 24, alpha=0.1, color="gray")
    ax1.axvspan(0, 6, alpha=0.1, color="gray")

    # Panel 2: Encounter Phase
    ax2 = axes[1]
    phase_order = ["Early", "Middle", "Late"]
    phase = temporal_df.groupby("encounter_phase").agg(
        temp_rate=("temp_present", "mean"),
        hr_rate=("hr_present", "mean"),
    ).reindex(phase_order)

    xp = np.arange(len(phase_order))
    width = 0.35
    bars1 = ax2.bar(xp - width / 2, phase["temp_rate"] * 100, width, label="Temperature", color="coral")
    bars2 = ax2.bar(xp + width / 2, phase["hr_rate"] * 100, width, label="Heart Rate", color="steelblue")
    ax2.set_xlabel("Encounter Phase", fontsize=11)
    ax2.set_ylabel("Presence Rate (%)", fontsize=11)
    ax2.set_title("Vital Presence by Encounter Phase", fontsize=12, fontweight="bold")
    ax2.set_xticks(xp)
    ax2.set_xticklabels(phase_order)
    ax2.legend(fontsize=9)
    ax2.set_ylim(0, 105)
    for bar, rate in zip(bars1, phase["temp_rate"] * 100):
        ax2.annotate(
            f"{rate:.1f}%",
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
            ha="center", va="bottom", fontsize=9,
        )

    # Panel 3: Day of Week
    ax3 = axes[2]
    dow_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    dow = temporal_df.groupby("day_of_week").agg(
        temp_rate=("temp_present", "mean"),
        hr_rate=("hr_present", "mean"),
    ).reset_index()
    dow["day_label"] = dow["day_of_week"].map(dict(enumerate(dow_labels)))

    ax3.bar(dow["day_label"], dow["temp_rate"] * 100, color="coral", alpha=0.8, label="Temperature")
    ax3.plot(
        dow["day_label"], dow["hr_rate"] * 100,
        "o-", color="steelblue", linewidth=2, markersize=8, label="Heart Rate",
    )
    ax3.set_xlabel("Day of Week", fontsize=11)
    ax3.set_ylabel("Presence Rate (%)", fontsize=11)
    ax3.set_title("Vital Presence by Day of Week", fontsize=12, fontweight="bold")
    ax3.legend(fontsize=9)
    ax3.set_ylim(0, 105)

    plt.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------


def test_mcar_chi_square(miss_df: pd.DataFrame) -> dict:
    """Chi-square test: is temperature missingness independent of other vitals?

    Returns dict with keys: chi2, p_value, dof, contingency, reject_mcar.
    """
    other_complete = (
        (miss_df["hr_present"] == 1)
        & (miss_df["rr_present"] == 1)
        & (miss_df["spo2_present"] == 1)
        & (miss_df["sbp_present"] == 1)
        & (miss_df["dbp_present"] == 1)
    ).astype(int)

    contingency = pd.crosstab(
        miss_df["temp_present"].map({0: "Temp Missing", 1: "Temp Present"}),
        other_complete.map({0: "Others Incomplete", 1: "Others Complete"}),
    )

    chi2, p_value, dof, expected = chi2_contingency(contingency)

    return {
        "chi2": chi2,
        "p_value": p_value,
        "dof": dof,
        "contingency": contingency,
        "reject_mcar": p_value < 0.05,
    }


def test_conditional_distributions(values_df: pd.DataFrame) -> pd.DataFrame:
    """T-test + KS-test comparing vital distributions when temp present vs absent.

    Parameters
    ----------
    values_df : DataFrame from the ``conditional_values`` query, with columns
        ``temp_present``, ``hr_value``, ``rr_value``, ``spo2_value``,
        ``sbp_value``, ``dbp_value``.

    Returns
    -------
    DataFrame with one row per vital and columns for test statistics.
    """
    vitals_to_test = [
        ("hr_value", "Heart Rate"),
        ("rr_value", "Respiratory Rate"),
        ("spo2_value", "SpO2"),
        ("sbp_value", "Systolic BP"),
        ("dbp_value", "Diastolic BP"),
    ]

    results = []
    for col, name in vitals_to_test:
        data = values_df[values_df[col].notna()].copy()
        present = data[data["temp_present"] == 1][col].values
        absent = data[data["temp_present"] == 0][col].values

        if len(present) > 0 and len(absent) > 0:
            t_stat, t_pval = ttest_ind(present, absent)
            ks_stat, ks_pval = ks_2samp(present, absent)
            pooled_std = np.sqrt((np.var(present) + np.var(absent)) / 2)
            cohens_d = (
                (np.mean(present) - np.mean(absent)) / pooled_std
                if pooled_std > 0
                else 0
            )
            results.append(
                {
                    "Vital": name,
                    "Mean (Temp Present)": np.mean(present),
                    "Mean (Temp Absent)": np.mean(absent),
                    "t-statistic": t_stat,
                    "t p-value": t_pval,
                    "KS statistic": ks_stat,
                    "KS p-value": ks_pval,
                    "Cohen's d": cohens_d,
                    "n_present": len(present),
                    "n_absent": len(absent),
                }
            )

    return pd.DataFrame(results)
