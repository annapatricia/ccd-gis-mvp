# CCD – Open Drug-Use Scenes (GIS MVP) 

Open drug-use scenes represent a persistent challenge for urban governance in large metropolitan areas. Public security interventions frequently aim to reduce visibility and concentration, yet their spatial consequences remain contested.

## Research Objective

This project develops a reproducible spatial-analytical framework to assess how public security policies shape the territorial dynamics of open drug-use scenes.

The central question is not only whether interventions reduce visible drug-use activity, but how they reconfigure it spatially.

The framework evaluates:

- **Spatial configuration:** how enforcement actions reshape hotspot formation and clustering patterns  
- **Displacement dynamics:** whether interventions generate territorial spillovers rather than suppression  
- **Spatial concentration:** how unequal the distribution of events remains after policy action  
- **Qualitative mechanisms (conceptual layer):** how institutional practices and on-the-ground dynamics help explain observed spatial shifts  

The repository runs with **synthetic georeferenced data by default**, ensuring methodological transparency and reproducibility. The structure is designed to be adapted to restricted administrative datasets (e.g., police or municipal security records).


---

## Analytical Contributions of the MVP

This MVP operationalizes a policy-evaluation framework that integrates spatial analysis, causal inference, and qualitative interpretation.

### Spatial Policy Diagnostics

- **Hexagonal spatial aggregation (H3):** standardized territorial units for comparing intervention areas over time  
- **Hotspot analysis:** identification of clustering patterns before and after enforcement actions  
- **Displacement metrics:** centroid shifts and spatial dispersion indicators to detect geographic relocation  
- **Concentration measures:** Top-k share and spatial Gini coefficients to assess inequality in event distribution  

### Quasi-Experimental Policy Evaluation

- **Event-study and Difference-in-Differences (DiD):** estimation of intervention effects over time  
- **Spatial spillover analysis:** ring/buffer models to evaluate indirect territorial effects  

### Qualitative Mechanisms (Pilot Layer)

- **Semi-structured interview guide:** targeting security agents, municipal managers, outreach workers, and affected populations  
- **Initial coding framework:** displacement mechanisms, collateral effects, and integrated governance approaches  


---

##  Repository structure
```
ccd-gis-mvp/
│
├── data/
│ ├── raw/ # original or restricted datasets (not versioned)
│ └── processed/ # cleaned and aggregated spatial data
│
├── notebooks/ # exploratory analysis (optional)
├── src/ # reproducible scripts (main pipeline)
│
├── reports/
│ ├── figures/ # static outputs (PNG, PDF)
│ └── maps/ # interactive HTML maps
│
├── qualitative/
│ └── protocols/ # interview guides and coding frameworks
│
├── docs/ # project documentation
└── README.md
```

---

## Reproducibility Guide

To replicate the analytical workflow:

Create environment (Windows):
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Run full pipeline:
python src/run_mvp.py

Alternatively, run step by step using notebooks:
- notebooks/01_synthetic_data.ipynb
- notebooks/02_hotspots.ipynb
- notebooks/03_event_study_spillover.ipynb

Outputs are saved in:
- reports/maps/
- reports/figures/
- data/processed/
---

## Data & Ethical Considerations

- Raw point-level geolocated data should not be publicly released when referring to sensitive populations or vulnerable territories.  
- Public dissemination should rely on spatial aggregation (e.g., H3 hexagonal grids) and anonymization procedures.  
- This repository is structured to operate with **synthetic georeferenced data** to ensure transparency, reproducibility, and ethical compliance.  
- When adapted to restricted administrative datasets, data access and storage should follow institutional and legal protocols.


## Interactive Maps (São Paulo – Synthetic Scenario)

Event-level visualization:

[Open synthetic events map](reports/maps/synthetic_events_map_sao_paulo.html)

Hexagonal hotspot aggregation (H3):

[Open H3 hotspot map](reports/maps/h3_hotspots_res9_sao_paulo.html)

## Results

### Time Series (Daily Events)

![Daily events time series](reports/figures/timeseries_daily_events.png)

### H3 Hotspots — Before vs After

The hexagonal aggregation (H3) highlights spatial concentration patterns before and after the intervention.

[Open interactive H3 hotspot map](reports/maps/h3_hotspots_res9_sao_paulo.html)

<p align="center">
  <img src="reports/figures/h3_hotspots_pre.png" width="48%" />
  <img src="reports/figures/h3_hotspots_post.png" width="48%" />
</p>

**Pre-intervention:** higher concentration around the initial hotspot.  
**Post-intervention:** spatial displacement toward a new territorial cluster.

### Spatial Concentration and Inequality

To assess whether intervention reduced territorial concentration or merely displaced it, we compute both the Top-10% concentration share and the Spatial Gini coefficient.

**Top 10% most active cells:**
- Pre-intervention: **69.87%** of events  
- Post-intervention: **59.27%** of events  
- Total (combined): **38.67%**

**Spatial Gini coefficient:**
- Pre-intervention: **0.838**
- Post-intervention: **0.775**
- Total (combined): **0.616**

Results indicate that although spatial inequality decreases after intervention, concentration remains high. This suggests partial dispersion combined with territorial displacement rather than full suppression.

### Causal Estimate (Difference-in-Differences)

We estimate a two-way fixed effects Difference-in-Differences model with:

- H3 cell fixed effects
- Day fixed effects
- Standard errors clustered at the cell level

Main result:

Treat × Post coefficient = **−1.67 events per cell-day**  
(p < 0.001)

This indicates that treated cells experienced a statistically significant reduction in event intensity after the intervention.

Full results table available in:
data/processed/did_results.csv

### Dynamic Effects (Event Study)

The event-study specification estimates dynamic treatment effects relative to the intervention date (day 0), using:

- H3 cell fixed effects
- Day fixed effects
- Clustered standard errors at the cell level

![Event Study](reports/figures/event_study_did.png)

Pre-intervention coefficients remain close to zero, supporting the parallel trends assumption. 

Post-intervention estimates show a sustained and statistically significant reduction in event intensity within treated cells, consistent with a localized enforcement effect.

