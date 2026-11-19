"""Shared helpers for every clustering model (written by the team lead).

Unsupervised learning has NO target. Before any model sees the data we therefore

1. REMOVE the labelled / outcome columns (``is_cancelled``, ``reservation_status``, ...),
2. keep only the booking-behaviour features,
3. log-transform skewed counts and standardise everything (clustering is distance based).

The removed labels are only used AFTER clustering, to describe each cluster ("what share of
this cluster cancelled?"). They never influence which booking lands in which cluster.

Why numeric features only? We tested adding one-hot encoded text columns: the silhouette score
fell from 0.37 to 0.27 because 0/1 dummy columns dominate the distances. Two text columns
(hotel and market segment) are used in the cluster profile instead.
"""

import time
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from sklearn.decomposition import PCA  # noqa: E402
from sklearn.metrics import (  # noqa: E402
    adjusted_rand_score, calinski_harabasz_score, davies_bouldin_score,
    silhouette_score)
from sklearn.preprocessing import StandardScaler  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA_PATH = ROOT / "output" / "analysis_ready_hotel_bookings.csv"
RESULTS_DIR = HERE / "results"
METRICS_DIR = RESULTS_DIR / "metrics"
CHARTS_DIR = RESULTS_DIR / "charts"
PROFILES_DIR = RESULTS_DIR / "profiles"

SEED = 42
SAMPLE_FOR_SCORES = 10000          # silhouette needs all pairwise distances -> use a sample
K_RANGE = range(3, 9)              # candidate numbers of clusters (k=2 is excluded, see below)

# Columns that carry the outcome or the answer. They are removed BEFORE clustering.
LABEL_COLUMNS = ["is_cancelled", "reservation_status", "reservation_status_date",
                 "realized_revenue", "estimated_revenue"]

INK, MUTED, GRID, SURFACE = "#1f2933", "#6b7280", "#e5e7eb", "#fcfcfb"
# Validated categorical slots 1-5 (blue, orange, aqua, yellow, magenta). Contrast against the
# surface is below 3:1 for three of them, so every chart also prints the cluster NUMBER.
CLUSTER_COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4",
                  "#008300", "#6250d6", "#e34948"]
NOISE_COLOR = "#9ca3af"


@dataclass
class Prepared:
    """Everything a model needs: scaled matrix, feature names and the aligned raw rows."""
    X: np.ndarray            # standardised feature matrix (rows = bookings)
    names: list              # feature names in column order
    data: pd.DataFrame       # the same rows with ALL original columns (labels included)


def load_data(path=DATA_PATH):
    """Read the analysis-ready CSV created by ``python pipeline.py``."""
    if not Path(path).exists():
        raise SystemExit(f"{path} not found. Run `python pipeline.py` first.")
    return pd.read_csv(path)


def build_features(df):
    """Engineer the clustering features from a table that has ALREADY lost its labels."""
    f = pd.DataFrame({
        "lead_time_log": np.log1p(df["lead_time"]),
        "total_nights": df["total_nights"],
        "avg_daily_rate": df["avg_daily_rate"],
        "total_guests": df["total_guests"],
        "has_children": ((df["children"] + df["babies"]) > 0).astype(int),
        "special_requests": df["special_requests"],
        "booking_changes": df["booking_changes"].clip(upper=3),
        "prev_cancellations_log": np.log1p(df["previous_cancellations"]),
        "prev_kept_log": np.log1p(df["previous_bookings_kept"]),
        "is_repeat_guest": df["is_repeat_guest"],
        "has_agent": df["has_agent"],
        "has_company": df["has_company"],
        "waiting_days_log": np.log1p(df["waiting_days"]),
    })
    return f


def prepare(df, fast=False):
    """Remove labels, build features, standardise. ``fast=True`` uses 3,000 random rows."""
    if fast:
        df = df.sample(n=min(3000, len(df)), random_state=SEED)
    df = df.reset_index(drop=True)
    unlabelled = df.drop(columns=[c for c in LABEL_COLUMNS if c in df.columns])
    features = build_features(unlabelled)
    assert not set(LABEL_COLUMNS) & set(features.columns), "a label leaked into the features"
    X = StandardScaler().fit_transform(features)
    return Prepared(X=X, names=list(features.columns), data=df)


# ------------------------------------------------------------------ metrics
def evaluate(X, labels, seed=SEED):
    """Internal quality scores (no labels needed). Noise points (label -1) are ignored."""
    labels = np.asarray(labels)
    mask = labels >= 0
    ids, counts = np.unique(labels[mask], return_counts=True)
    out = {"n_clusters": int(len(ids)),
           "noise_pct": round(100 * float((~mask).mean()), 1),
           "smallest_cluster_pct": round(100 * float(counts.min() / len(labels)), 2)
           if len(ids) else 0.0,
           "largest_cluster_pct": round(100 * float(counts.max() / len(labels)), 1)
           if len(ids) else 0.0}
    if len(ids) < 2:
        out.update(silhouette=np.nan, davies_bouldin=np.nan, calinski_harabasz=np.nan)
        return out
    Xm, lm = X[mask], labels[mask]
    out["silhouette"] = round(float(silhouette_score(
        Xm, lm, sample_size=min(SAMPLE_FOR_SCORES, len(Xm)), random_state=seed)), 4)
    out["davies_bouldin"] = round(float(davies_bouldin_score(Xm, lm)), 3)
    out["calinski_harabasz"] = round(float(calinski_harabasz_score(Xm, lm)), 0)
    return out


def stability(fit_labels, X, seeds=(1, 2, 3)):
    """Mean adjusted Rand index between runs with different seeds (1.0 = identical)."""
    runs = [np.asarray(fit_labels(s)) for s in seeds]
    return round(float(np.mean([adjusted_rand_score(runs[0], r) for r in runs[1:]])), 3)


def choose_k(table):
    """Pick k from a table with columns k, silhouette, davies_bouldin.

    Rank k by silhouette (higher is better) and by Davies-Bouldin (lower is better), add the
    ranks, and take the smallest total (ties -> smaller k). Using two scores avoids trusting
    one noisy number.
    """
    t = table.copy()
    t["rank"] = (t["silhouette"].rank(ascending=False, method="min")
                 + t["davies_bouldin"].rank(ascending=True, method="min"))
    return int(t.sort_values(["rank", "k"]).iloc[0]["k"])


# ------------------------------------------------------------------ profile
def profile(df, labels):
    """One row per cluster: size and the average of the readable columns.

    ``cancel_rate`` uses the label that was removed before clustering. It is for
    interpretation only and was never seen by the model.
    """
    g = df.assign(cluster=np.asarray(labels))
    rows = g.groupby("cluster").agg(
        bookings=("cluster", "size"),
        lead_time=("lead_time", "mean"),
        total_nights=("total_nights", "mean"),
        avg_daily_rate=("avg_daily_rate", "mean"),
        total_guests=("total_guests", "mean"),
        share_with_children=("children", lambda s: (s > 0).mean()),
        special_requests=("special_requests", "mean"),
        booking_changes=("booking_changes", "mean"),
        share_repeat_guest=("is_repeat_guest", "mean"),
        share_with_agent=("has_agent", "mean"),
        share_with_company=("has_company", "mean"),
        avg_waiting_days=("waiting_days", "mean"),
        share_resort_hotel=("hotel", lambda s: (s == "resort hotel").mean()),
        cancel_rate=("is_cancelled", "mean"))
    rows.insert(1, "share_of_bookings", rows["bookings"] / len(g))
    return rows.round(3).reset_index()


# ------------------------------------------------------------------- charts
def _style():
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE, "axes.edgecolor": GRID,
        "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
        "text.color": INK, "axes.titlecolor": INK, "axes.titleweight": "bold",
        "axes.titlelocation": "left", "axes.spines.top": False,
        "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
        "axes.axisbelow": True, "font.size": 10})


def save_chart(fig, name, suffix):
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    path = CHARTS_DIR / f"{name}_{suffix}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def _color(c):
    return NOISE_COLOR if c < 0 else CLUSTER_COLORS[c % len(CLUSTER_COLORS)]


def plot_clusters(name, title, X, labels):
    """2-D PCA view: each dot is a booking, colour = cluster, number = cluster centre."""
    _style()
    labels = np.asarray(labels)
    pca = PCA(n_components=2, random_state=SEED).fit(X)
    Z = pca.transform(X)
    idx = np.random.RandomState(SEED).choice(len(Z), min(8000, len(Z)), replace=False)
    fig, ax = plt.subplots(figsize=(8, 5.6))
    for c in sorted(set(labels)):
        m = labels[idx] == c
        label = "Noise" if c < 0 else f"Cluster {c + 1}"
        share = 100 * (labels == c).mean()
        ax.scatter(Z[idx][m, 0], Z[idx][m, 1], s=6, alpha=0.45, color=_color(c),
                   edgecolors="none", label=f"{label} ({share:.0f}%)")
        if c >= 0:
            cx, cy = Z[labels == c].mean(axis=0)
            ax.text(cx, cy, str(c + 1), ha="center", va="center", fontsize=12,
                    fontweight="bold", color=INK,
                    bbox={"boxstyle": "circle,pad=0.25", "fc": SURFACE, "ec": INK})
    ev = pca.explained_variance_ratio_
    ax.set_xlabel(f"Principal component 1 ({ev[0]:.0%} of variance)")
    ax.set_ylabel(f"Principal component 2 ({ev[1]:.0%} of variance)")
    ax.set_title(title, pad=22)
    ax.text(0, 1.03, "Each dot is a booking, numbers mark cluster centres",
            transform=ax.transAxes, color=MUTED, fontsize=9.5)
    ax.legend(frameon=False, markerscale=3, loc="best")
    return save_chart(fig, name, "clusters")


def plot_profile(name, title, X, names, labels):
    """Heat map of standardised feature averages per cluster (what makes each cluster special)."""
    _style()
    labels = np.asarray(labels)
    ids = sorted(c for c in set(labels) if c >= 0)
    M = np.vstack([X[labels == c].mean(axis=0) for c in ids])
    lim = min(4.0, max(1.0, float(np.abs(M).max())))      # colours saturate at +-4 std. dev.
    cmap = LinearSegmentedColormap.from_list("div", ["#eb6834", "#e5e7eb", "#2a78d6"])
    fig, ax = plt.subplots(figsize=(10, 0.8 + 0.7 * len(ids)))
    im = ax.imshow(M, cmap=cmap, vmin=-lim, vmax=lim, aspect="auto")
    ax.grid(False)
    ax.set_xticks(range(len(names)), names, rotation=40, ha="right", fontsize=9)
    ax.set_yticks(range(len(ids)), [f"Cluster {c + 1}" for c in ids])
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            ax.text(j, i, f"{M[i, j]:.1f}", ha="center", va="center", fontsize=8,
                    color=INK)
    for s in ax.spines.values():
        s.set_visible(False)
    cb = fig.colorbar(im, ax=ax, shrink=0.9)
    cb.set_label("Std. deviations from the overall average (colour capped at 4)")
    ax.set_title(title, pad=10)
    return save_chart(fig, name, "profile")


# ------------------------------------------------------------------ results
def make_result(name, params, metrics, started, notes=""):
    """The dictionary every model's ``run()`` returns."""
    return {"model": name, "params": str(params), "seconds": round(time.time() - started, 1),
            "notes": notes, **metrics}


def save_result(result, profile_table=None):
    """Write ``results/metrics/<model>.csv`` (+ the cluster profile if given)."""
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    path = METRICS_DIR / f"{result['model']}.csv"
    pd.DataFrame([result]).to_csv(path, index=False)
    if profile_table is not None:
        PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        profile_table.to_csv(PROFILES_DIR / f"{result['model']}_profile.csv", index=False)
    return path
