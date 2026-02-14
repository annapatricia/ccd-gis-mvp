import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

import folium
import matplotlib.pyplot as plt


# ---------- paths ----------
ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_OUT = os.path.join(ROOT, "data", "processed")
MAP_OUT = os.path.join(ROOT, "reports", "maps")
FIG_OUT = os.path.join(ROOT, "reports", "figures")

os.makedirs(DATA_OUT, exist_ok=True)
os.makedirs(MAP_OUT, exist_ok=True)
os.makedirs(FIG_OUT, exist_ok=True)

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

