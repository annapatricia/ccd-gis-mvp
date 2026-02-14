from shapely.geometry import Polygon
from shapely.geometry import mapping

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

import folium
import h3
from shapely.geometry import Polygon

import matplotlib.pyplot as plt


# ---------- paths ----------
ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_OUT = os.path.join(ROOT, "data", "processed")
MAP_OUT = os.path.join(ROOT, "reports", "maps")
FIG_OUT = os.path.join(ROOT, "reports", "figures")

os.makedirs(DATA_OUT, exist_ok=True)
os.makedirs(MAP_OUT, exist_ok=True)
os.makedirs(FIG_OUT, exist_ok=True)

# ---------- helpers ----------
def h3_to_polygon(h):
    boundary = h3.cell_to_boundary(h)  # returns (lat, lon) pairs in this version
    # shapely expects (x, y) = (lon, lat)
    return Polygon([(lon, lat) for lat, lon in boundary])

# ---------- synthetic data ----------
np.random.seed(42)

# "City center" (example coordinates – use generic coords, not sensitive)
center_lat, center_lon = -23.5364, -46.6330  # Região da Luz (SP)

n_events = 1500

start = datetime(2025, 10, 1)
days = 90

dates = [start + timedelta(days=int(x)) for x in np.random.randint(0, days, n_events)]

# create two hotspots that shift after an "operation" date
op_date = datetime(2025, 11, 10)

lat = np.zeros(n_events)
lon = np.zeros(n_events)

for i in range(n_events):
    if dates[i] < op_date:
        # hotspot A
        lat[i] = np.random.normal(center_lat + 0.010, 0.003)
        lon[i] = np.random.normal(center_lon - 0.010, 0.004)
    else:
        # shift to hotspot B (displacement)
        lat[i] = np.random.normal(center_lat - 0.008, 0.004)
        lon[i] = np.random.normal(center_lon + 0.012, 0.004)

df = pd.DataFrame({
    "event_id": range(1, n_events + 1),
    "date": pd.to_datetime(dates),
    "lat": lat,
    "lon": lon,
})
df["period"] = np.where(df["date"] < op_date, "pre", "post")

# ---------- H3 grid ----------
H3_RES = 9  # ~170m hex edges (good for neighborhood-level patterns)
try:
    df["h3"] = df.apply(lambda r: h3.latlng_to_cell(r["lat"], r["lon"], H3_RES), axis=1)
except AttributeError:
    df["h3"] = df.apply(lambda r: h3.geo_to_h3(r["lat"], r["lon"], H3_RES), axis=1)


# counts per H3 cell and period
cell_counts = (
    df.groupby(["h3", "period"])
      .size()
      .rename("events")
      .reset_index()
)
cell_wide = (
    cell_counts.pivot(index="h3", columns="period", values="events")
    .fillna(0)
    .reset_index()
)



if "pre" not in cell_wide.columns:
    cell_wide["pre"] = 0
if "post" not in cell_wide.columns:
    cell_wide["post"] = 0

cell_wide["total"] = cell_wide["pre"] + cell_wide["post"]

cells_csv = os.path.join(DATA_OUT, f"h3_counts_res{H3_RES}.csv")
cell_wide.to_csv(cells_csv, index=False)

# ---------- concentration metrics ----------

def concentration_top_percent(df_cells, col, pct=0.10):
    df_sorted = df_cells.sort_values(col, ascending=False)
    n_top = max(1, int(len(df_sorted) * pct))

    top_sum = df_sorted.head(n_top)[col].sum()
    total_sum = df_sorted[col].sum()

    if total_sum == 0:
        return 0.0

    return 100 * top_sum / total_sum

pre_conc = concentration_top_percent(cell_wide, "pre", pct=0.10)
post_conc = concentration_top_percent(cell_wide, "post", pct=0.10)
total_conc = concentration_top_percent(cell_wide, "total", pct=0.10)



csv_path = os.path.join(DATA_OUT, "synthetic_events.csv")
df.to_csv(csv_path, index=False)




# ---------- displacement distance (Haversine) ----------
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

pre = df[df["period"] == "pre"]
post = df[df["period"] == "post"]

pre_lat, pre_lon = pre["lat"].mean(), pre["lon"].mean()
post_lat, post_lon = post["lat"].mean(), post["lon"].mean()

disp_km = haversine_km(pre_lat, pre_lon, post_lat, post_lon)



# ---------- interactive map ----------
m = folium.Map(location=[center_lat, center_lon], zoom_start=12, control_scale=True)

# sample points for visualization only
sample = df.sample(min(400, len(df)), random_state=42)

for _, r in sample.iterrows():
    color = "blue" if r["period"] == "pre" else "red"
    folium.CircleMarker(
        location=[r["lat"], r["lon"]],
        radius=3,
        color=color,
        fill=True,
        fill_opacity=0.6
    ).add_to(m)

folium.LayerControl().add_to(m)

map_path = os.path.join(MAP_OUT, "synthetic_events_map_sao_paulo.html")


m.save(map_path)

# ---------- hotspot hex map (H3) ----------

def add_hex_layer(map_obj, df_hex, value_col, layer_name, show_layer=False):
    layer = folium.FeatureGroup(name=layer_name, show=show_layer)
    vmax = df_hex[value_col].max() if df_hex[value_col].max() > 0 else 1

    for _, row in df_hex.iterrows():
        h = row["h3"]
        val = float(row[value_col])

        boundary = h3.cell_to_boundary(h)

        # detect order: (lat,lon) vs (lon,lat)
        a, b = boundary[0]
        if abs(a) <= 90 and abs(b) <= 180:
            # boundary is (lat, lon) -> shapely wants (lon, lat)
            coords = [(lon, lat) for (lat, lon) in boundary]
        else:
            # boundary is (lon, lat)
            coords = [(lon, lat) for (lon, lat) in boundary]

        # close ring
        if coords[0] != coords[-1]:
            coords.append(coords[0])

        # build polygon and fix self-intersections (this prevents "triangles")
        poly = Polygon(coords)
        if not poly.is_valid:
            poly = poly.buffer(0)

        if poly.is_empty:
            continue

        intensity = val / vmax
        shade = int(220 * (1 - intensity))
        fill_color = f"#ff{shade:02x}{shade:02x}"

        gj = {
            "type": "Feature",
            "properties": {
                value_col: int(val)
            },
            "geometry": mapping(poly)
        }

        folium.GeoJson(
            gj,
            style_function=lambda x, fc=fill_color: {
                "fillColor": fc,
                "color": "#000000",
                "weight": 0.2,
                "fillOpacity": 0.55,
            },
            tooltip=f"{layer_name}: {int(val)}"
        ).add_to(layer)

    layer.add_to(map_obj)

# ---------- build and save H3 hotspot map ----------
m_hex = folium.Map(location=[center_lat, center_lon], zoom_start=12, control_scale=True)

hex_pre = cell_wide[["h3", "pre"]].copy()
hex_post = cell_wide[["h3", "post"]].copy()
hex_total = cell_wide[["h3", "total"]].copy()

add_hex_layer(m_hex, hex_total, "total", "Hotspots (Total)", show_layer=True)
add_hex_layer(m_hex, hex_pre, "pre", "Hotspots (Pre)", show_layer=False)
add_hex_layer(m_hex, hex_post, "post", "Hotspots (Post)", show_layer=False)

folium.LayerControl().add_to(m_hex)

hex_map_path = os.path.join(MAP_OUT, f"h3_hotspots_res{H3_RES}_sao_paulo.html")
m_hex.save(hex_map_path)



# ---------- time series plot (daily counts) ----------
daily = df.set_index("date").resample("D").size().rename("events").reset_index()

plt.figure()
plt.plot(daily["date"], daily["events"])
plt.axvline(op_date, linestyle="--")  # intervention date
plt.title("Synthetic events over time (São Paulo scenario)")
plt.xlabel("Date")
plt.ylabel("Number of events (daily)")
plt.xticks(rotation=45)
plt.tight_layout()

ts_path = os.path.join(FIG_OUT, "timeseries_daily_events.png")
plt.savefig(ts_path, dpi=200)
plt.close()


print("✅ Done")
print("CSV:", csv_path)
print("Map:", map_path)

print(f"Displacement (pre -> post): {disp_km:.2f} km")
print(f"Pre centroid:  ({pre_lat:.5f}, {pre_lon:.5f})")
print(f"Post centroid: ({post_lat:.5f}, {post_lon:.5f})")
print("Time series figure:", ts_path)
print("Intervention date:", op_date.date()) 
print("H3 counts CSV:", cells_csv)
print("H3 hotspot map:", hex_map_path)
print("\n--- Spatial concentration (Top 10% cells) ---")
print(f"Pre:  {pre_conc:.2f}% of events")
print(f"Post: {post_conc:.2f}% of events")
print(f"Total:{total_conc:.2f}% of events")



