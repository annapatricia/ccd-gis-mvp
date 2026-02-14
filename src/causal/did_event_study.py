import os
import pandas as pd
import numpy as np

# ---------- paths ----------
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_PATH = os.path.join(ROOT, "data", "processed", "synthetic_events.csv")

# ---------- load data ----------
df = pd.read_csv(DATA_PATH, parse_dates=["date"])

# ---------- define intervention date ----------
intervention_date = pd.to_datetime("2025-11-10")

df["post"] = (df["date"] >= intervention_date).astype(int)

# ---------- aggregate to H3 x day ----------
panel = (
    df.groupby(["h3", "date"])
      .size()
      .rename("events")
      .reset_index()
)

# fill missing combinations (balanced panel)
all_cells = panel["h3"].unique()
all_dates = panel["date"].unique()

full_index = pd.MultiIndex.from_product(
    [all_cells, all_dates],
    names=["h3", "date"]
)
panel = (
    panel.set_index(["h3", "date"])
         .reindex(full_index, fill_value=0)
         .reset_index()
)

# post indicator
panel["post"] = (panel["date"] >= intervention_date).astype(int)

# ---------- define treated cells (top 10% pre-period cells) ----------
pre_counts = (
    df[df["date"] < intervention_date]
      .groupby("h3")
      .size()
      .rename("pre_events")
      .reset_index()
)

threshold = np.quantile(pre_counts["pre_events"], 0.90)
treated_cells = pre_counts.loc[pre_counts["pre_events"] >= threshold, "h3"].tolist()

panel["treat"] = panel["h3"].isin(treated_cells).astype(int)

# ---------- quick checks ----------
print("Panel created")
print(panel.head())
print(f"Treated cells: {panel['treat'].sum()} (out of {panel['h3'].nunique()})")

# ---------- DiD with Two-Way Fixed Effects ----------
from linearmodels.panel import PanelOLS

panel["did"] = panel["treat"] * panel["post"]

panel = panel.set_index(["h3", "date"])

y = panel["events"]
X = panel[["did"]]

model = PanelOLS(y, X, entity_effects=True, time_effects=True)
results = model.fit(cov_type="clustered", cluster_entity=True)

print("\n--- Difference-in-Differences Results ---")
print(results.summary)

# ---------- Save main DiD result ----------
coef = results.params["did"]
se = results.std_errors["did"]
tstat = results.tstats["did"]
pval = results.pvalues["did"]
ci = results.conf_int()
ci_lower = ci.loc["did"].iloc[0]
ci_upper = ci.loc["did"].iloc[1]


did_table = pd.DataFrame({
    "coefficient": [coef],
    "std_error": [se],
    "t_stat": [tstat],
    "p_value": [pval],
    "ci_lower": [ci_lower],
    "ci_upper": [ci_upper]
})

output_path = os.path.join(ROOT, "data", "processed", "did_results.csv")
did_table.to_csv(output_path, index=False)

print("\nDiD results saved to:", output_path)

# ---------- Event study (dynamic effects) ----------
import matplotlib.pyplot as plt

# Reset index back to columns (PanelOLS needs MultiIndex later)
panel_es = panel.reset_index().copy()

# relative day to intervention
panel_es["rel_day"] = (panel_es["date"] - intervention_date).dt.days

# choose event window (paper standard)
WINDOW_PRE = 21
WINDOW_POST = 21
panel_es = panel_es[(panel_es["rel_day"] >= -WINDOW_PRE) & (panel_es["rel_day"] <= WINDOW_POST)].copy()

# create event-time dummies interacted with treat
# baseline will be rel_day = -1 (omitted)
baseline = -1
event_days = [d for d in range(-WINDOW_PRE, WINDOW_POST + 1) if d != baseline]

for d in event_days:
    panel_es[f"es_{d}"] = ((panel_es["rel_day"] == d) & (panel_es["treat"] == 1)).astype(int)

# panel index
panel_es = panel_es.set_index(["h3", "date"])

y_es = panel_es["events"]
X_cols = [f"es_{d}" for d in event_days]
X_es = panel_es[X_cols]

es_model = PanelOLS(y_es, X_es, entity_effects=True, time_effects=True)
es_res = es_model.fit(cov_type="clustered", cluster_entity=True)

# build results table for plotting
rows = []
for d in event_days:
    name = f"es_{d}"
    rows.append({
        "rel_day": d,
        "coef": float(es_res.params[name]),
        "se": float(es_res.std_errors[name]),
    })

es_df = pd.DataFrame(rows).sort_values("rel_day")
es_df["ci_low"] = es_df["coef"] - 1.96 * es_df["se"]
es_df["ci_high"] = es_df["coef"] + 1.96 * es_df["se"]

# save table
es_out = os.path.join(ROOT, "data", "processed", "event_study_results.csv")
es_df.to_csv(es_out, index=False)
print("\nEvent study results saved to:", es_out)

# plot
plt.figure()
plt.plot(es_df["rel_day"], es_df["coef"])
plt.axvline(0, linestyle="--")      # intervention
plt.axhline(0, linestyle="--")      # zero effect
plt.fill_between(es_df["rel_day"], es_df["ci_low"], es_df["ci_high"], alpha=0.2)
plt.title("Event Study: Dynamic Effects (Treat × Event Time)")
plt.xlabel("Days relative to intervention")
plt.ylabel("Effect on events per cell-day")
plt.tight_layout()

fig_path = os.path.join(ROOT, "reports", "figures", "event_study_did.png")
plt.savefig(fig_path, dpi=200)
plt.close()
print("Event study figure saved to:", fig_path)

# ---------- Spillover (radial exposure) ----------
import h3
from math import radians, cos, sin, asin, sqrt

# helper: haversine distance in km
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

# compute centroid of pre-treatment hotspot
treated_pre = df[(df["date"] < intervention_date) & (df["h3"].isin(treated_cells))]
center_lat = treated_pre["lat"].mean()
center_lon = treated_pre["lon"].mean()

# compute distance of each H3 cell centroid to hotspot center
cell_coords = []

for cell in panel_es.reset_index()["h3"].unique():
    boundary = h3.cell_to_boundary(cell)
    lat = np.mean([p[0] for p in boundary])
    lon = np.mean([p[1] for p in boundary])
    dist = haversine_km(lat, lon, center_lat, center_lon)
    cell_coords.append((cell, dist))

dist_df = pd.DataFrame(cell_coords, columns=["h3", "distance_km"])

panel_spill = panel.reset_index().merge(dist_df, on="h3")

# define rings (in km)
panel_spill["ring_0_05"] = (panel_spill["distance_km"] <= 0.5).astype(int)
panel_spill["ring_05_1"] = ((panel_spill["distance_km"] > 0.5) & (panel_spill["distance_km"] <= 1.0)).astype(int)
panel_spill["ring_1_15"] = ((panel_spill["distance_km"] > 1.0) & (panel_spill["distance_km"] <= 1.5)).astype(int)

panel_spill["ring_0_05_post"] = panel_spill["ring_0_05"] * panel_spill["post"]
panel_spill["ring_05_1_post"] = panel_spill["ring_05_1"] * panel_spill["post"]
panel_spill["ring_1_15_post"] = panel_spill["ring_1_15"] * panel_spill["post"]

panel_spill = panel_spill.set_index(["h3", "date"])

y_sp = panel_spill["events"]
X_sp = panel_spill[["ring_0_05_post", "ring_05_1_post", "ring_1_15_post"]]

spill_model = PanelOLS(y_sp, X_sp, entity_effects=True, time_effects=True)
spill_res = spill_model.fit(cov_type="clustered", cluster_entity=True)

print("\n--- Spillover Results ---")
print(spill_res.summary)

# ---------- Save spillover results ----------
spill_params = spill_res.params
spill_se = spill_res.std_errors
spill_t = spill_res.tstats
spill_p = spill_res.pvalues
spill_ci = spill_res.conf_int()

spill_rows = []
for var in ["ring_0_05_post", "ring_05_1_post", "ring_1_15_post"]:
    spill_rows.append({
        "term": var,
        "coefficient": float(spill_params[var]),
        "std_error": float(spill_se[var]),
        "t_stat": float(spill_t[var]),
        "p_value": float(spill_p[var]),
        "ci_lower": float(spill_ci.loc[var].iloc[0]),
        "ci_upper": float(spill_ci.loc[var].iloc[1]),
    })

spill_table = pd.DataFrame(spill_rows)

spill_out = os.path.join(ROOT, "data", "processed", "spillover_results.csv")
spill_table.to_csv(spill_out, index=False)

print("\nSpillover results saved to:", spill_out)



