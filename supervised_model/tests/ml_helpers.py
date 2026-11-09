"""Helpers shared by the machine-learning tests (a small fake dataset, no real data needed)."""

import numpy as np
import pandas as pd

from supervised_model import common


def make_ml_df(n=1200, seed=0):
    """A fake 'analysis-ready' table with every column the models use."""
    rng = np.random.RandomState(seed)
    lead = rng.gamma(2.0, 40, n).round()
    adr = (60 + 0.1 * lead + rng.normal(0, 25, n)).clip(0, 300)
    p_cancel = 1 / (1 + np.exp(-(lead - 80) / 60))
    data = {
        "is_cancelled": (rng.rand(n) < p_cancel).astype(int),
        "avg_daily_rate": adr.round(2),
        "hotel": rng.choice(["city hotel", "resort hotel"], n),
        "season": rng.choice(["winter", "spring", "summer", "autumn"], n),
        "meal": rng.choice(["bb", "hb", "sc"], n),
        "country": rng.choice(["PRT", "GBR", "FRA", "ESP"], n),
        "market_segment": rng.choice(["online ta", "direct", "groups"], n),
        "distribution_channel": rng.choice(["ta/to", "direct"], n),
        "reserved_room_type": rng.choice(["a", "d", "e"], n),
        "deposit_type": rng.choice(["no deposit", "non refund"], n, p=[0.95, 0.05]),
        "customer_type": rng.choice(["transient", "contract"], n),
        "guest_group": rng.choice(["solo", "couple", "family"], n),
        "lead_time": lead,
    }
    for c in common.NUMERIC:
        if c not in data:
            data[c] = rng.randint(0, 4, n)
    return pd.DataFrame(data)


def redirect_outputs(monkeypatch, tmp_path):
    """Make a test write its metrics/charts to a temp folder instead of the repository."""
    monkeypatch.setattr(common, "RESULTS_DIR", tmp_path)
    monkeypatch.setattr(common, "METRICS_DIR", tmp_path / "metrics")
    monkeypatch.setattr(common, "CHARTS_DIR", tmp_path / "charts")
