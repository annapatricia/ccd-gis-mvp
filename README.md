# CCD – Open Drug-Use Scenes (GIS MVP)

**Goal:** build a reproducible GIS + statistics MVP to study how **public security policies** affect:
- **spatial configuration** (hotspots, clustering),
- **mobility/displacement** (spillovers),
- **concentration** (spatial inequality of events),
with a **light qualitative layer** to explain mechanisms.

> This repository is structured to run with **synthetic data by default** and can later be adapted to restricted datasets.

---

## ? What this MVP delivers
### Spatial analytics
- Hex grid (H3) aggregation
- Hotspot detection (KDE / Gi*)
- Displacement metrics (centroid shift, radius / dispersion)
- Concentration metrics (Top-k share, spatial Gini)

### Causal / quasi-experimental
- Event-study / Difference-in-Differences (DiD)
- Spatial spillovers (rings / buffers)

### Qualitative (pilot layer)
- Interview guide (security, managers, outreach, users)
- Initial coding schema (displacement, collateral effects, integrated approaches)

---

## ?? Repository structure
\\\
ccd-gis-mvp/
+-- data/
¦   +-- raw/
¦   +-- processed/
+-- notebooks/
+-- src/
+-- reports/
¦   +-- figures/
¦   +-- maps/
+-- qualitative/
¦   +-- protocols/
+-- docs/
+-- README.md
\\\

---

## ?? Quickstart
1) Create environment
\\\ash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
\\\

2) Run notebooks
- 
otebooks/01_synthetic_data.ipynb
- 
otebooks/02_hotspots.ipynb
- 
otebooks/03_event_study_spillover.ipynb

---

## ?? Data & ethics
- Do not publish raw point-level sensitive geolocations.
- Use aggregation (H3/hex) and anonymization for any public release.
- This repository is designed to work with **synthetic data** for open sharing.

## Interactive map (São Paulo – synthetic scenario)
[Open synthetic events map](reports/maps/synthetic_events_map_sao_paulo.html)

resultados
### ?? Time series (daily events)

![Daily events time series](reports/figures/timeseries_daily_events.png)

## ?? H3 Hotspots — Before vs After

<p align="center">
  <img src="reports/figures/h3_hotspots_pre.png" width="48%" />
  <img src="reports/figures/h3_hotspots_post.png" width="48%" />
</p>

**Pre:** Higher concentration around the initial hotspot.  
**Post:** Spatial displacement after intervention.
