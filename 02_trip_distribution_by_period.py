import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
import os

warnings.filterwarnings("ignore")
os.makedirs("figures", exist_ok=True)

# ── CONFIG ─────────────────────────────────────────────────────────────────────
DATA_DIR = r"C:\Users\wilon\Documents\TU DELFT\THESIS\DATA\fluctuo_data"
CELLS_FILE = os.path.join(DATA_DIR, "fluctuo_cell_trips.csv")

# ── Load ───────────────────────────────────────────────────────────────────────
cells = pd.read_csv(CELLS_FILE)
cells["total_trips"] = (
    cells["incoming_trips"] +
    cells["outgoing_trips"] +
    cells["internal_trips"]
)

CITIES  = sorted(cells["city"].unique())
PERIODS = ["6month", "1year"]

PALETTE = {
    "6month": "#2E75B6",   # blue
    "1year":  "#E63946",   # red
}

TRIP_TYPES = {
    "incoming_trips": "Incoming Trips",
    "outgoing_trips": "Outgoing Trips",
    "internal_trips": "Internal Trips",
}

# ══════════════════════════════════════════════════════════════════════════════
# One figure per trip type — 5 cities × 2 periods side by side
# ══════════════════════════════════════════════════════════════════════════════
for col, label in TRIP_TYPES.items():
    fig, axes = plt.subplots(1, len(CITIES), figsize=(18, 5), sharey=False)
    fig.suptitle(
        f"Distribution of {label} per City — 6month vs 1year",
        fontsize=10, fontweight="bold"
    )

    for ax, city in zip(axes, CITIES):
        for period in PERIODS:
            d = cells[(cells["city"] == city) & (cells["period"] == period)][col]

            # Use percentile-clipped bins for cleaner histograms
            vmax = d.quantile(0.98)
            bins = np.linspace(0, vmax, 40)

            ax.hist(
                d.clip(upper=vmax),
                bins=bins,
                color=PALETTE[period],
                alpha=0.55,
                edgecolor="white",
                linewidth=0.3,
                label=period,
            )
            ax.axvline(
                d.median(),
                color=PALETTE[period],
                linewidth=1.8,
                linestyle="--",
                alpha=0.9,
            )

        ax.set_title(city.capitalize(), fontsize=10, fontweight="bold")
        ax.set_xlabel("Trips (mean/day)", fontsize=9)
        ax.set_ylabel("Number of cells", fontsize=9)
        ax.tick_params(labelsize=8)
        ax.grid(axis="y", alpha=0.3)

        # Annotation: median values
        for period in PERIODS:
            d = cells[(cells["city"] == city) & (cells["period"] == period)][col]
            ax.text(
                0.97, 0.97 if period == "6month" else 0.88,
                f"{period} med: {d.median():.3f}",
                transform=ax.transAxes,
                ha="right", va="top",
                fontsize=8,
                color=PALETTE[period],
                fontweight="bold",
            )

    # Legend on first axis only
    axes[0].legend(fontsize=9, title="Period", loc="center right")

    plt.tight_layout()
    fname = f"figures/Trip Data Exploration/02_trip_dist_{col}.png"
    plt.savefig(fname, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved → {fname}")

# ══════════════════════════════════════════════════════════════════════════════
# Summary table: median per city per period per trip type
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("MEDIAN TRIPS PER CITY PER PERIOD")
print("="*80)

rows = []
for city in CITIES:
    for period in PERIODS:
        c = cells[(cells["city"] == city) & (cells["period"] == period)]
        rows.append({
            "city":           city,
            "period":         period,
            "n_cells":        len(c),
            "med_incoming":   round(c["incoming_trips"].median(), 4),
            "med_outgoing":   round(c["outgoing_trips"].median(), 4),
            "med_internal":   round(c["internal_trips"].median(), 4),
            "med_total":      round(c["total_trips"].median(),    4),
        })

df = pd.DataFrame(rows)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)
print(df.to_string(index=False))

df.to_csv("trip_distribution_by_period.csv", index=False)
print("\nSaved → trip_distribution_by_period.csv")
print("Done.")
