"""Train every model and compare them.

    python -m supervised_model.train_models                  # all models (about 1.5 min)
    python -m supervised_model.train_models --only knn svm   # only some models
    python -m supervised_model.train_models --fast           # 3,000-row demo (seconds)

Models that are still stubs (NotImplementedError) are skipped, so the script works while the
team is still merging. Results: supervised_model/results/metrics/*.csv,
supervised_model/results/model_comparison.csv and charts in supervised_model/results/charts/.
"""

import argparse
import importlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from supervised_model import common  # noqa: E402

MODULES = {
    "linear_regression": "supervised_model.member1_linear_regression",
    "logistic_regression": "supervised_model.member2_logistic_regression",
    "knn": "supervised_model.member3_knn",
    "svm": "supervised_model.member3_svm",
    "decision_tree": "supervised_model.member4_decision_tree",
    "random_forest": "supervised_model.member4_random_forest",
}
ORDER = list(MODULES)


def plot_comparison(res):
    """Grouped bars: accuracy, F1 and ROC-AUC of the classification models."""
    common._style()
    res = res.set_index("model")
    cols = ["accuracy", "f1", "roc_auc"]
    colors = [common.BLUE, common.ORANGE, "#1baf7a"]
    fig, ax = plt.subplots(figsize=(10, 4.6))
    x = np.arange(len(res))
    w = 0.26
    for i, (c, col) in enumerate(zip(cols, colors)):
        bars = ax.bar(x + (i - 1) * w, res[c], w, color=col, label=c.upper().replace("_", "-"))
        for b, v in zip(bars, res[c]):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.01, f"{v:.2f}", ha="center",
                    fontsize=8, color=common.INK)
    ax.axhline(res["baseline_accuracy"].iloc[0], color=common.MUTED, ls="--", lw=1,
               label="Baseline accuracy (always predict 'kept')")
    pretty = {"knn": "KNN", "svm": "SVM"}
    ax.set_xticks(x, [pretty.get(m, m.replace("_", " ").title()) for m in res.index])
    ax.set_ylim(0, 1.05)
    ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=4)
    ax.set_title("Classification models: cancellation prediction (test set)", pad=34)
    fig.tight_layout()
    common.CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    path = common.CHARTS_DIR / "model_comparison.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def run_all(only=None, fast=False):
    df = common.load_data()
    results, skipped = [], []
    for name in ORDER:
        if only and name not in only:
            continue
        module = importlib.import_module(MODULES[name])
        try:
            print(f"training {name} ...", flush=True)
            r = module.run(df, fast=fast)
        except NotImplementedError:
            skipped.append(name)
            print("  skipped (not implemented yet)")
            continue
        results.append(r)
        print(f"  done in {r['seconds']}s")
    if not results:
        print("No model implemented yet.")
        return pd.DataFrame()
    table = pd.DataFrame(results)
    common.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(common.RESULTS_DIR / "model_comparison.csv", index=False)
    clf = table[table.task == "classification"]
    if len(clf):
        plot_comparison(clf)
    show = ["model", "task", "accuracy", "precision", "recall", "f1", "roc_auc", "mae",
            "rmse", "r2", "seconds"]
    print("\n" + table[[c for c in show if c in table]].fillna("").to_string(index=False))
    if skipped:
        print("\nSkipped:", ", ".join(skipped))
    return table


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", choices=ORDER)
    ap.add_argument("--fast", action="store_true")
    a = ap.parse_args()
    run_all(a.only, a.fast)
