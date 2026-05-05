"""
00_data_description.py
======================
Describes the structure and features of both Fluctuo datasets.
Produces a clean summary table for each dataset.

OUTPUT:
  data_description_cells.csv   — cell-level dataset summary
  data_description_flows.csv   — flow-level dataset summary
"""

import pandas as pd
import numpy as np

# ── Load ───────────────────────────────────────────────────────────────────────
flows = pd.read_csv("fluctuo_raw_flows.csv")
cells = pd.read_csv("fluctuo_cell_trips.csv")

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

# ══════════════════════════════════════════════════════════════════════════════
# DATASET 1: fluctuo_cell_trips.csv
# ══════════════════════════════════════════════════════════════════════════════
print("=" * 80)
print("DATASET 1: fluctuo_cell_trips.csv")
print("=" * 80)

print(f"""
OVERVIEW
  Total rows         : {len(cells):,}
  Total columns      : {len(cells.columns)}
  Cities             : {', '.join(sorted(cells['city'].unique()))}
  Time periods       : {', '.join(sorted(cells['period'].unique()))}
  H3 resolution      : {cells['h3_resolution'].unique()[0]} (hexagon ~350m diameter)
  Zone type          : {cells['zone'].unique()[0]} (all cells are H3 resolution 9)
""")

print("COLUMN DESCRIPTIONS!")
col_desc = {
    "h3_index":       ("str",     "Unique H3 hexagon identifier"),
    "city":           ("str",     "City name (bologna, valencia, toulouse, bern, bratislava)"),
    "period":         ("str",     "Observation period (6month or 1year)"),
    "zone":           ("str",     "H3 zone type (always h3_9)"),
    "lat":            ("float",   "Centroid latitude of H3 cell (WGS84)"),
    "lon":            ("float",   "Centroid longitude of H3 cell (WGS84)"),
    "h3_resolution":  ("int",     "H3 grid resolution (always 9)"),
    "incoming_trips": ("float",   "Mean daily trips arriving at this cell"),
    "outgoing_trips": ("float",   "Mean daily trips departing from this cell"),
    "internal_trips": ("float",   "Mean daily trips starting AND ending in this cell"),
}
print(f"  {'Column':<22} {'Type':<8} {'Description'}")
print(f"  {'-'*70}")
for col, (dtype, desc) in col_desc.items():
    print(f"  {col:<22} {dtype:<8} {desc}")

print("\nCELLS PER CITY PER PERIOD")
pivot = cells.groupby(["city", "period"]).size().unstack()
pivot["total (both periods)"] = pivot.sum(axis=1)
print(pivot.to_string())

print("\nTRIP VALUE RANGES (6month period)")
c6 = cells[cells["period"] == "6month"]
rows = []
for col in ["incoming_trips", "outgoing_trips", "internal_trips"]:
    s = c6[col]
    rows.append({
        "variable":  col,
        "min":       round(s.min(),    4),
        "max":       round(s.max(),    4),
        "mean":      round(s.mean(),   4),
        "median":    round(s.median(), 4),
        "std":       round(s.std(),    4),
        "n_zeros":   int((s == 0).sum()),
        "pct_zeros": round((s == 0).mean() * 100, 1),
    })
print(pd.DataFrame(rows).to_string(index=False))

cells_out = pd.DataFrame(rows)
cells_out.to_csv("data_description_cells.csv", index=False)
print("\nSaved → data_description_cells.csv")

# ══════════════════════════════════════════════════════════════════════════════
# DATASET 2: fluctuo_raw_flows.csv
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("DATASET 2: fluctuo_raw_flows.csv")
print("=" * 80)

# Distance
flows_od = flows[flows["from_code"] != flows["to_code"]].copy()
flows_od["dist_km"] = np.sqrt(
    (flows_od["from_lat"] - flows_od["to_lat"])**2 +
    (flows_od["from_lon"] - flows_od["to_lon"])**2
) * 111

print(f"""
OVERVIEW
  Total rows         : {len(flows):,}
  Total columns      : {len(flows.columns)}
  Cities             : {', '.join(sorted(flows['city'].unique()))}
  Time periods       : {', '.join(sorted(flows['period'].unique()))}
  Self-loops (same cell) : {(flows['from_code']==flows['to_code']).sum():,}
  OD pairs (different cells): {(flows['from_code']!=flows['to_code']).sum():,}
""")

print("COLUMN DESCRIPTIONS")
col_desc2 = {
    "city":      ("str",   "City name"),
    "period":    ("str",   "Observation period (6month or 1year)"),
    "from_code": ("str",   "H3 index of origin cell"),
    "from_lat":  ("float", "Centroid latitude of origin cell (WGS84)"),
    "from_lon":  ("float", "Centroid longitude of origin cell (WGS84)"),
    "to_code":   ("str",   "H3 index of destination cell"),
    "to_lat":    ("float", "Centroid latitude of destination cell (WGS84)"),
    "to_lon":    ("float", "Centroid longitude of destination cell (WGS84)"),
    "mean":      ("float", "Mean daily flow between origin and destination cell"),
}
print(f"  {'Column':<12} {'Type':<8} {'Description'}")
print(f"  {'-'*60}")
for col, (dtype, desc) in col_desc2.items():
    print(f"  {col:<12} {dtype:<8} {desc}")

print("\nOD PAIRS PER CITY (6month, self-loops excluded)")
f6 = flows[(flows["period"] == "6month") & (flows["from_code"] != flows["to_code"])]
rows2 = []
for city in sorted(f6["city"].unique()):
    d = f6[f6["city"] == city]
    dist = flows_od[flows_od["city"] == city]["dist_km"]
    rows2.append({
        "city":           city,
        "n_od_pairs":     len(d),
        "mean_flow_min":  round(d["mean"].min(),    4),
        "mean_flow_max":  round(d["mean"].max(),    4),
        "mean_flow_avg":  round(d["mean"].mean(),   4),
        "dist_median_km": round(dist.median(),      2),
        "dist_max_km":    round(dist.max(),         2),
    })
df2 = pd.DataFrame(rows2)
print(df2.to_string(index=False))

df2.to_csv("data_description_flows.csv", index=False)
print("\nSaved → data_description_flows.csv")

print("\n" + "=" * 80)
print("COMBINED OVERVIEW")
print("=" * 80)
print(f"""
  fluctuo_cell_trips  : {len(cells):,} rows × {len(cells.columns)} columns
  fluctuo_raw_flows   : {len(flows):,} rows × {len(flows.columns)} columns
  Cities              : 5 (Bologna, Valencia, Toulouse, Bern, Bratislava)
  Time periods        : 2 (6month, 1year)
  Spatial unit        : H3 hexagon resolution 9 (~350m diameter)
  Trip values         : mean daily trips (aggregated over observation period)
  Flow values         : mean daily OD flow between cell pairs
""")
print("Done.")
