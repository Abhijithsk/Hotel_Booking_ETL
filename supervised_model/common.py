"""Shared helpers for every model (written by the team lead).

All six models use the SAME data preparation, the SAME train/test split and the SAME metrics,
so their results can be compared fairly.

Two prediction tasks
--------------------
* regression      -> target ``avg_daily_rate`` (price per night)         : Linear Regression
* classification  -> target ``is_cancelled`` (1 = booking was cancelled) : Logistic Regression,
                                                                           KNN, SVM,
                                                                           Decision Tree,
                                                                           Random Forest

Data leakage (very important)
-----------------------------
A model may only use information that is known when the prediction is made. We therefore never
use: ``reservation_status`` / ``reservation_status_date`` (they contain the answer),
``realized_revenue`` / ``estimated_revenue`` (computed from price and the answer), and the
columns that only exist after arrival (``assigned_room_type``, ``room_changed``,
``parking_spaces``): a cancelled booking never gets a room or a parking space.
"""

import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.compose import ColumnTransformer  # noqa: E402
from sklearn.metrics import (  # noqa: E402
    accuracy_score, confusion_matrix, f1_score, mean_absolute_error,
    mean_squared_error, precision_score, r2_score, recall_score, roc_auc_score,
    roc_curve)
from sklearn.model_selection import train_test_split  # noqa: E402
from sklearn.preprocessing import OneHotEncoder, StandardScaler  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA_PATH = ROOT / "output" / "analysis_ready_hotel_bookings.csv"
RESULTS_DIR = HERE / "results"
METRICS_DIR = RESULTS_DIR / "metrics"
CHARTS_DIR = RESULTS_DIR / "charts"

SEED = 42
TEST_SIZE = 0.2

TARGETS = {"regression": "avg_daily_rate", "classification": "is_cancelled"}

CATEGORICAL = ["hotel", "season", "meal", "country", "market_segment",
               "distribution_channel", "reserved_room_type", "deposit_type",
               "customer_type", "guest_group"]
NUMERIC = ["lead_time", "arrival_year", "arrival_month", "arrival_week", "arrival_day",
           "weekend_nights", "week_nights", "adults", "children", "babies", "total_guests",
           "total_nights", "is_repeat_guest", "previous_cancellations",
           "previous_bookings_kept", "booking_changes", "has_agent", "has_company",
           "waiting_days", "special_requests"]

# Columns that must never be used as inputs (see the module docstring).
LEAKAGE = ["reservation_status", "reservation_status_date", "realized_revenue",
           "estimated_revenue", "assigned_room_type", "room_changed", "parking_spaces"]

INK, MUTED, GRID, SURFACE = "#1f2933", "#6b7280", "#e5e7eb", "#fcfcfb"
BLUE, ORANGE = "#2a78d6", "#eb6834"


def load_data(path=DATA_PATH):
    """Read the analysis-ready CSV created by ``python pipeline.py``."""
    if not Path(path).exists():
        raise SystemExit(f"{path} not found. Run `python pipeline.py` first.")
    return pd.read_csv(path)


def feature_lists(task):
    """Return (numeric_columns, categorical_columns) for a task."""
    if task not in TARGETS:
        raise ValueError("task must be 'regression' or 'classification'")
    numeric = list(NUMERIC)
    if task == "classification":
        numeric.append("avg_daily_rate")       # the price is known at booking time
    assert not set(numeric + CATEGORICAL) & set(LEAKAGE)
    return numeric, list(CATEGORICAL)


def build_preprocessor(task, scale=True):
    """Scale numbers (needed by KNN/SVM/linear models) and one-hot encode text columns.

    Rare categories (fewer than 50 rows, e.g. small countries) are grouped together.
    """
    numeric, categorical = feature_lists(task)
    num = StandardScaler() if scale else "passthrough"
    cat = OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=50,
                        sparse_output=False)
    return ColumnTransformer([("num", num, numeric), ("cat", cat, categorical)])


def prepare(df, task, fast=False):
    """Split into train/test (80/20, fixed seed, stratified for classification).

    ``fast=True`` uses a 3,000-row sample so unit tests run in seconds.
    """
    numeric, categorical = feature_lists(task)
    target = TARGETS[task]
    if fast:
        df = df.sample(n=min(3000, len(df)), random_state=SEED)
    X, y = df[numeric + categorical], df[target]
    return train_test_split(X, y, test_size=TEST_SIZE, random_state=SEED,
                            stratify=y if task == "classification" else None)


# ------------------------------------------------------------------ metrics
def classification_metrics(y_true, y_pred, y_score):
    """Accuracy, precision, recall, F1 and ROC-AUC (cancelled = positive class)."""
    base = max(float(np.mean(y_true)), 1 - float(np.mean(y_true)))
    return {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_true, y_pred, zero_division=0), 4),
        "f1": round(f1_score(y_true, y_pred, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(y_true, y_score), 4),
        "baseline_accuracy": round(base, 4),   # always predicting the majority class
    }


def regression_metrics(y_true, y_pred, y_train_mean):
    """MAE, RMSE and R2, plus the RMSE of always predicting the training mean."""
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    base = float(np.sqrt(mean_squared_error(y_true, np.full(len(y_true), y_train_mean))))
    return {
        "mae": round(mean_absolute_error(y_true, y_pred), 2),
        "rmse": round(rmse, 2),
        "r2": round(r2_score(y_true, y_pred), 4),
        "baseline_rmse": round(base, 2),
    }


def feature_names(fitted_pipeline):
    """Column names after preprocessing (needed for coefficients/importances)."""
    return list(fitted_pipeline.named_steps["prep"].get_feature_names_out())


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


def _save(fig, name, suffix):
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    path = CHARTS_DIR / f"{name}_{suffix}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_classification(name, title, y_true, y_pred, y_score):
    """Confusion matrix (counts) and ROC curve side by side."""
    _style()
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    cm = confusion_matrix(y_true, y_pred)
    ax = axes[0]
    ax.imshow(cm, cmap="Blues")
    ax.grid(False)
    for (i, j), v in np.ndenumerate(cm):
        ax.text(j, i, f"{v:,}", ha="center", va="center", fontsize=12,
                color="white" if v > cm.max() / 2 else INK)
    ax.set_xticks([0, 1], ["Kept", "Cancelled"])
    ax.set_yticks([0, 1], ["Kept", "Cancelled"])
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(f"{title}: confusion matrix")
    fpr, tpr, _ = roc_curve(y_true, y_score)
    ax = axes[1]
    ax.plot(fpr, tpr, color=BLUE, lw=2, label=f"AUC = {roc_auc_score(y_true, y_score):.3f}")
    ax.plot([0, 1], [0, 1], color=MUTED, ls="--", lw=1, label="Random guess")
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.set_title(f"{title}: ROC curve")
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    return _save(fig, name, "evaluation")


def plot_regression(name, title, y_true, y_pred):
    """Actual vs predicted price and the residual histogram."""
    _style()
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    ax = axes[0]
    idx = np.random.RandomState(SEED).choice(len(y_true), min(3000, len(y_true)),
                                             replace=False)
    ax.scatter(np.asarray(y_true)[idx], np.asarray(y_pred)[idx], s=6, alpha=0.35,
               color=BLUE, edgecolors="none")
    lim = [0, max(np.max(y_true), np.max(y_pred))]
    ax.plot(lim, lim, color=ORANGE, lw=1.5, label="Perfect prediction")
    ax.set_xlabel("Actual daily rate (EUR)")
    ax.set_ylabel("Predicted daily rate (EUR)")
    ax.set_title(f"{title}: actual vs predicted")
    ax.legend(frameon=False, loc="upper left")
    ax = axes[1]
    ax.hist(np.asarray(y_true) - np.asarray(y_pred), bins=50, color=BLUE, rwidth=0.9)
    ax.axvline(0, color=INK, ls="--", lw=1)
    ax.set_xlabel("Error = actual - predicted (EUR)")
    ax.set_ylabel("Bookings")
    ax.set_title(f"{title}: residuals")
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return _save(fig, name, "evaluation")


def plot_importance(name, title, names, values, top=15, label="Importance"):
    """Horizontal bars of the ``top`` features by absolute value."""
    _style()
    s = pd.Series(values, index=names)
    s = s.reindex(s.abs().sort_values(ascending=False).index)[:top][::-1]
    fig, ax = plt.subplots(figsize=(8, 5.2))
    ax.barh(s.index, s.values, color=BLUE, height=0.65)
    ax.set_xlabel(label)
    ax.grid(axis="y", visible=False)
    ax.set_title(f"{title}: top {len(s)} features")
    fig.tight_layout()
    return _save(fig, name, "importance")


def plot_curve(name, title, x, y, xlabel, ylabel, best=None):
    """A simple line chart (e.g. accuracy against k)."""
    _style()
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(x, y, color=BLUE, lw=2, marker="o", ms=6, markeredgecolor=SURFACE)
    if best is not None:
        ax.axvline(best, color=ORANGE, ls="--", lw=1.2)
        ax.text(best, ax.get_ylim()[0], f" best = {best}", color=INK, va="bottom")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    fig.tight_layout()
    return _save(fig, name, "tuning")


# ------------------------------------------------------------------ results
def make_result(name, task, metrics, params, started, notes=""):
    """Build the dictionary every model's ``run()`` returns."""
    return {"model": name, "task": task, "params": str(params),
            "seconds": round(time.time() - started, 1), "notes": notes, **metrics}


def save_result(result):
    """Write one line per model to ``supervised_model/results/metrics/<model>.csv``."""
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    path = METRICS_DIR / f"{result['model']}.csv"
    pd.DataFrame([result]).to_csv(path, index=False)
    return path
