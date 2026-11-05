"""Exploratory Data Analysis (EDA) for the Hotel Booking ETL project.

Reads the analysis-ready dataset produced by the ETL pipeline and saves the
main plots to ``output/eda/``.

Run:
    python eda.py            # makes all charts
    python eda.py --show     # also prints the key numbers

Only pandas, numpy and matplotlib are needed (already in requirements.txt).
Leakage columns (``reservation_status``, ``reservation_status_date`` and
``realized_revenue``) are NOT used to explain cancellations.
"""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "output" / "analysis_ready_hotel_bookings.csv"
OUT = ROOT / "output" / "eda"

# Validated palette (scripts/validate_palette). Fixed order: city, resort.
BLUE, ORANGE, GREEN = "#2a78d6", "#eb6834", "#1baf7a"
HOTEL_COLOR = {"city hotel": BLUE, "resort hotel": ORANGE}
INK, MUTED, GRID, SURFACE = "#1f2933", "#6b7280", "#e5e7eb", "#fcfcfb"

LEAKAGE = ["reservation_status", "reservation_status_date", "realized_revenue"]


def _style():
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE, "axes.edgecolor": GRID,
        "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
        "text.color": INK, "axes.titlecolor": INK, "axes.titlesize": 13,
        "axes.titleweight": "bold", "axes.titlelocation": "left",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
        "axes.axisbelow": True, "font.size": 10, "figure.dpi": 100,
    })


def load_data(path=DATA):
    if not Path(path).exists():
        raise SystemExit(f"{path} not found. Run `python pipeline.py` first.")
    return pd.read_csv(path, parse_dates=["arrival_date"])


def _save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return OUT / name


def _title(ax, title, sub=None):
    ax.set_title(title, pad=22 if sub else 10)
    if sub:
        ax.text(0, 1.03, sub, transform=ax.transAxes, color=MUTED, fontsize=9.5)


def _rate(df, col, min_n=0):
    g = df.groupby(col, observed=True).agg(
        n=("is_cancelled", "size"), rate=("is_cancelled", "mean"))
    g["rate"] *= 100
    return g[g.n >= min_n]


def _hbar(ax, labels, values, ns, overall, fmt="{:.1f}%"):
    y = np.arange(len(labels))
    ax.barh(y, values, color=BLUE, height=0.6)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.axvline(overall, color=MUTED, lw=1, ls="--")
    for yi, v, n in zip(y, values, ns):
        ax.text(v + 0.6, yi, f"{fmt.format(v)}  (n={n:,})", va="center",
                color=INK, fontsize=9,
                bbox={"fc": SURFACE, "ec": "none", "pad": 1})
    ax.set_xlim(0, max(values) * 1.35)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Cancellation rate (%)")


# --------------------------------------------------------------- 1. overview
def plot_overview(df):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), gridspec_kw={"width_ratios": [1, 1.4]})
    overall = df.is_cancelled.mean() * 100
    ax = axes[0]
    r = _rate(df, "hotel")
    labels = ["All bookings"] + [h.title() for h in r.index]
    vals = [overall] + list(r.rate)
    ax.bar(labels, vals, color=[MUTED, BLUE, BLUE], width=0.55)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.8, f"{v:.1f}%", ha="center", fontweight="bold")
    ax.set_ylim(0, 40)
    ax.set_ylabel("Cancellation rate (%)")
    ax.grid(axis="x", visible=False)
    _title(ax, "Cancellations", "Share of bookings cancelled")
    ax = axes[1]
    ax.hist(df.total_nights, bins=np.arange(0.5, 15.5, 1), color=BLUE, rwidth=0.85)
    ax.axvline(df.total_nights.median(), color=INK, lw=1, ls="--")
    ax.text(df.total_nights.median() + 0.2, ax.get_ylim()[1] * 0.92,
            f"median {df.total_nights.median():.0f} nights", color=INK)
    ax.set_xlabel("Nights stayed (capped at 15 for display)")
    ax.set_ylabel("Bookings")
    ax.grid(axis="x", visible=False)
    _title(ax, "Length of stay", "Most stays are short")
    return _save(fig, "01_overview.png")


# ------------------------------------------------------- 2. bookings by month
def plot_monthly_bookings(df):
    m = df.groupby(["arrival_year_month", "hotel"]).size().unstack()
    fig, ax = plt.subplots(figsize=(11, 4.2))
    x = np.arange(len(m))
    for h in m.columns:
        ax.plot(x, m[h], color=HOTEL_COLOR[h], lw=2, label=h.title())
        ax.text(x[-1] + 0.3, m[h].iloc[-1], h.split()[0].title(),
                color=INK, va="center", fontsize=9)
    ticks = list(range(0, len(m), 3))
    ax.set_xticks(ticks, [m.index[i] for i in ticks], rotation=45, ha="right")
    ax.set_xlim(-0.5, len(m) + 2)
    ax.set_ylim(0)
    ax.set_ylabel("Bookings arriving")
    ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, loc="upper left")
    _title(ax, "Bookings by arrival month",
           "Both hotels grow; the city hotel pulls ahead from early 2016")
    return _save(fig, "02_monthly_bookings.png")


# ---------------------------------------------------------- 3. price seasonality
def plot_price_seasonality(df):
    p = df.groupby(["arrival_month", "hotel"]).avg_daily_rate.mean().unstack()
    names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    fig, ax = plt.subplots(figsize=(9, 4.2))
    for h in p.columns:
        ax.plot(p.index, p[h], color=HOTEL_COLOR[h], lw=2, marker="o", ms=5,
                label=h.title(), markeredgecolor=SURFACE)
    ax.set_xticks(range(1, 13), names)
    ax.set_ylim(0)
    ax.set_ylabel("Average daily rate (EUR)")
    ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, loc="upper left")
    _title(ax, "Price seasonality",
           "Resort rates jump in August; city rates stay flatter")
    return _save(fig, "03_price_seasonality.png")


# -------------------------------------------------------- 4. distributions
def plot_distributions(df):
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
    for ax, (col, lab, bins) in zip(axes, [
            ("lead_time", "Lead time (days)", 40),
            ("avg_daily_rate", "Average daily rate (EUR)", 40),
            ("total_guests", "Guests per booking", np.arange(0.5, 6.5, 1))]):
        ax.hist(df[col], bins=bins, color=BLUE, rwidth=0.9)
        med = df[col].median()
        ax.axvline(med, color=INK, ls="--", lw=1)
        ax.text(0.97, 0.93, f"median {med:g}", transform=ax.transAxes,
                ha="right", color=INK, fontsize=9)
        ax.set_xlabel(lab)
        ax.grid(axis="x", visible=False)
    axes[0].set_ylabel("Bookings")
    fig.suptitle("Distributions of the main numeric columns (after outlier capping)",
                 x=0.01, ha="left", fontweight="bold", fontsize=13, y=1.03)
    return _save(fig, "04_distributions.png")


# ---------------------------------------------------- 5. price boxplot by hotel
def plot_price_by_hotel(df):
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    hotels = list(HOTEL_COLOR)
    data = [df.loc[df.hotel == h, "avg_daily_rate"] for h in hotels]
    bp = ax.boxplot(data, widths=0.5, patch_artist=True, showfliers=False,
                    medianprops={"color": INK, "lw": 2})
    for patch, h in zip(bp["boxes"], hotels):
        patch.set(facecolor=HOTEL_COLOR[h], alpha=0.85, edgecolor=SURFACE)
    ax.set_xticks([1, 2], [h.title() for h in hotels])
    ax.set_ylabel("Average daily rate (EUR)")
    ax.grid(axis="x", visible=False)
    for i, d in enumerate(data, 1):
        ax.text(i + 0.32, d.median(), f"median {d.median():.0f}",
                va="center", fontsize=9)
    _title(ax, "Price spread by hotel", "Box = middle 50% of bookings")
    return _save(fig, "05_price_by_hotel.png")


# -------------------------------------------------- 6. cancellation drivers
def plot_cancel_lead_time(df):
    order = ["0-7d", "8-30d", "31-90d", "91-180d", "180d+"]
    r = _rate(df, "lead_time_category").loc[order]
    overall = df.is_cancelled.mean() * 100
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.bar(order, r.rate, color=BLUE, width=0.6)
    for i, (v, n) in enumerate(zip(r.rate, r.n)):
        ax.text(i, v + 0.8, f"{v:.1f}%", ha="center", fontweight="bold")
        ax.text(i, 1.2, f"n={n:,}", ha="center", color=SURFACE, fontsize=8.5)
    ax.axhline(overall, color=MUTED, ls="--", lw=1)
    ax.text(-0.4, overall + 0.8, f"overall {overall:.1f}%", ha="left", color=MUTED)
    ax.set_ylim(0, 48)
    ax.set_ylabel("Cancellation rate (%)")
    ax.set_xlabel("Lead time (days between booking and arrival)")
    ax.grid(axis="x", visible=False)
    _title(ax, "Cancellations climb with lead time",
           "Last-minute bookings rarely cancel; 6+ month bookings often do")
    return _save(fig, "06_cancel_by_lead_time.png")


def plot_cancel_segments(df):
    overall = df.is_cancelled.mean() * 100
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
    r = _rate(df, "market_segment", 300).sort_values("rate", ascending=False)
    _hbar(axes[0], [s.title() for s in r.index], r.rate, r.n, overall)
    _title(axes[0], "By market segment", "Dashed line = overall rate")
    r = _rate(df, "country", 1500).sort_values("rate", ascending=False)
    _hbar(axes[1], r.index, r.rate, r.n, overall)
    _title(axes[1], "By guest country (12 biggest)", "Portugal, Brazil, Italy cancel most")
    fig.tight_layout()
    return _save(fig, "07_cancel_by_segment_country.png")


def plot_cancel_signals(df):
    """Four small multiples of behavioural signals (same y scale)."""
    overall = df.is_cancelled.mean() * 100
    specs = [
        ("deposit_type", "Deposit type", None),
        ("customer_type", "Customer type", None),
        ("guest_group", "Guest group", None),
        ("special_requests", "Special requests", lambda s: s.clip(upper=3).map(
            {0: "0", 1: "1", 2: "2", 3: "3+"})),
        ("room_changed", "Room changed at check-in", lambda s: s.map(
            {0: "No", 1: "Yes"})),
        ("is_repeat_guest", "Repeat guest", lambda s: s.map({0: "No", 1: "Yes"})),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(13, 7))
    for ax, (col, title, fn) in zip(axes.ravel(), specs):
        key = fn(df[col]) if fn else df[col]
        g = df.groupby(key, observed=True).agg(
            n=("is_cancelled", "size"), r=("is_cancelled", "mean"))
        g = g[g.n >= 100]
        g["r"] *= 100
        if col != "special_requests":
            g = g.sort_values("r", ascending=False)
        ax.bar([str(i) for i in g.index], g.r, color=BLUE, width=0.6)
        for i, v in enumerate(g.r):
            ax.text(i, v + 1.2, f"{v:.0f}%", ha="center", fontsize=9, fontweight="bold")
        ax.axhline(overall, color=MUTED, ls="--", lw=1)
        ax.set_ylim(0, 105)
        ax.set_title(title, fontsize=11)
        ax.grid(axis="x", visible=False)
        ax.tick_params(axis="x", labelsize=8.5)
    for ax in axes[:, 0]:
        ax.set_ylabel("Cancellation rate (%)")
    fig.suptitle("What separates cancellers from guests who stay? (dashed = overall 27.7%)",
                 x=0.01, ha="left", fontweight="bold", fontsize=13, y=0.995)
    fig.tight_layout()
    return _save(fig, "08_cancel_signals.png")


# ------------------------------------------------------------ 7. revenue
def plot_revenue(df):
    rev = df.groupby(["arrival_year_month", "hotel"]).realized_revenue.sum().unstack() / 1e6
    fig, ax = plt.subplots(figsize=(11, 4.2))
    x = np.arange(len(rev))
    for h in rev.columns:
        ax.plot(x, rev[h], color=HOTEL_COLOR[h], lw=2, label=h.title())
    ticks = list(range(0, len(rev), 3))
    ax.set_xticks(ticks, [rev.index[i] for i in ticks], rotation=45, ha="right")
    ax.set_ylim(0)
    ax.set_ylabel("Realized revenue (EUR million)")
    ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, loc="upper left")
    _title(ax, "Monthly realized revenue",
           "Revenue from kept bookings only (cancelled = 0)")
    return _save(fig, "09_monthly_revenue.png")


# ------------------------------------------------------------ 8. correlation
def plot_correlation(df):
    cols = ["is_cancelled", "lead_time", "avg_daily_rate", "total_nights",
            "total_guests", "special_requests", "booking_changes", "parking_spaces",
            "previous_cancellations", "previous_bookings_kept", "is_repeat_guest",
            "room_changed", "has_agent", "has_company", "waiting_days"]
    cols = [c for c in cols if c not in LEAKAGE]
    c = df[cols].corr()
    cmap = LinearSegmentedColormap.from_list(
        "div", [ORANGE, "#e5e7eb", BLUE])  # warm - gray midpoint - cool
    fig, ax = plt.subplots(figsize=(9, 7.5))
    im = ax.imshow(c, cmap=cmap, vmin=-1, vmax=1)
    ax.set_xticks(range(len(cols)), cols, rotation=60, ha="right", fontsize=8.5)
    ax.set_yticks(range(len(cols)), cols, fontsize=8.5)
    ax.grid(False)
    for i in range(len(cols)):
        for j in range(len(cols)):
            v = c.iloc[i, j]
            if abs(v) >= 0.2 and i != j:
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7.5, color=INK)
    cb = fig.colorbar(im, ax=ax, shrink=0.75)
    cb.set_label("Pearson correlation")
    for s in ax.spines.values():
        s.set_visible(False)
    _title(ax, "Correlation of numeric columns",
           "Blue = rise together, orange = move opposite. Leakage columns excluded")
    return _save(fig, "10_correlation.png")


ALL_PLOTS = [plot_overview, plot_monthly_bookings, plot_price_seasonality,
             plot_distributions, plot_price_by_hotel, plot_cancel_lead_time,
             plot_cancel_segments, plot_cancel_signals, plot_revenue,
             plot_correlation]


def run_eda(df=None, show=False):
    _style()
    df = load_data() if df is None else df
    paths = [fn(df) for fn in ALL_PLOTS]
    if show:
        print(f"{len(df):,} bookings, cancellation rate "
              f"{df.is_cancelled.mean():.1%}")
    print(f"EDA finished: {len(paths)} charts saved to {OUT}")
    return paths


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", action="store_true")
    run_eda(show=ap.parse_args().show)
