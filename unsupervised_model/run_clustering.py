"""Run every clustering model and compare them.

    python -m unsupervised_model.run_clustering                  # all models (about 1-2 minutes)
    python -m unsupervised_model.run_clustering --only kmeans    # selected models
    python -m unsupervised_model.run_clustering --fast           # 3,000-row demo (seconds)

Models that are still stubs (NotImplementedError) are skipped, so the script works while the
team is still merging. Results: unsupervised_model/results/ (metrics, profiles, charts,
model_comparison.csv).
"""

import argparse
import importlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from unsupervised_model import common  # noqa: E402

MODULES = {
    "kmeans": "unsupervised_model.member1_kmeans",
    "agglomerative": "unsupervised_model.member2_agglomerative",
    "gmm": "unsupervised_model.member3_gmm",
    "hdbscan": "unsupervised_model.member4_hdbscan",
}
ORDER = list(MODULES)
PRETTY = {"kmeans": "K-Means", "agglomerative": "Agglomerative", "gmm": "Gaussian Mixture",
          "hdbscan": "HDBSCAN"}


def plot_comparison(table):
    """Two bar charts: silhouette (higher is better) and Davies-Bouldin (lower is better)."""
    common._style()
    t = table.set_index("model")
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
    for ax, col, title in zip(axes, ["silhouette", "davies_bouldin"],
                              ["Silhouette (higher is better)",
                               "Davies-Bouldin (lower is better)"]):
        names = [PRETTY.get(m, m) for m in t.index]
        vals = t[col].fillna(0).values
        y = np.arange(len(names))
        ax.barh(y, vals, color=common.CLUSTER_COLORS[0], height=0.6)
        ax.set_yticks(y, names)
        ax.invert_yaxis()
        ax.grid(axis="y", visible=False)
        for yi, v, (_, r) in zip(y, vals, t.iterrows()):
            extra = f"  {int(r['n_clusters'])} clusters"
            if r["noise_pct"] > 0:
                extra += f", {r['noise_pct']:.0f}% noise"
            ax.text(v + 0.01 * max(vals.max(), 1), yi, f"{v:.2f}{extra}", va="center",
                    fontsize=9, color=common.INK)
        ax.set_xlim(0, max(vals.max(), 0.1) * 1.6)
        ax.set_title(title, fontsize=11)
    fig.tight_layout()
    fig.text(0.01, -0.03, "HDBSCAN is scored on a 15,000-booking sample and ignores its noise "
             "points, so its scores are not directly comparable.", color=common.MUTED,
             fontsize=8.5)
    return common.save_chart(fig, "model", "comparison")


def run_all(only=None, fast=False):
    df = common.load_data()
    results, skipped = [], []
    for name in ORDER:
        if only and name not in only:
            continue
        module = importlib.import_module(MODULES[name])
        try:
            print(f"clustering with {name} ...", flush=True)
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
    plot_comparison(table)
    show = ["model", "n_clusters", "silhouette", "davies_bouldin", "calinski_harabasz",
            "noise_pct", "smallest_cluster_pct", "stability_ari", "seconds"]
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
