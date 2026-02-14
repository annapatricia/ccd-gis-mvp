# CCD – Cenas Abertas de Uso de Drogas (GIS MVP)

This repository is a **minimal, reproducible MVP** to study how public security policies affect:
- **spatial configuration** of open drug-use scenes,
- **mobility/displacement** (spillover),
- **concentration** (hotspots),
combining **spatial statistics + quasi-experimental design** and a **light qualitative layer**.

## What this MVP delivers
- Spatial grid (H3/hex) + hotspot detection (KDE / Gi*)
- Event-study / DiD with spillover rings
- Displacement metrics (centroid shift, radius)
- Concentration metrics (top-k share / spatial Gini)
- Qualitative pilot layer: interview protocol + thematic coding template

## Repository Structure
- data/ raw & processed datasets (synthetic by default)
- src/ processing + spatial metrics + models
- 
otebooks/ EDA and experiments
- eports/ figures and interactive maps
- qualitative/ interview protocol + coding schema
- docs/ diagrams and methodology notes

## Next Steps
1. Add synthetic georeferenced events dataset
2. Generate hotspot maps (before/after)
3. Run event-study with spatial spillovers
4. Integrate qualitative mechanisms (pilot interviews)

