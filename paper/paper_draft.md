# The Spatial Effects of Security Interventions on Open Drug-Use Scenes

## Abstract

This study evaluates the causal impact of a targeted security intervention on the spatial concentration and redistribution of open drug-use scenes in an urban context. Using georeferenced event data aggregated at the H3 cell level, we implement a two-way fixed effects Difference-in-Differences (DiD) framework combined with event-study and radial spillover analyses. Results indicate a statistically significant reduction in event intensity within treated areas, with effects decaying over distance and no evidence of outward displacement in the synthetic scenario. These findings illustrate how spatial econometric tools can inform evidence-based public security policy.

---

## 1. Introduction

Open drug-use scenes represent a persistent challenge for urban governance. Public authorities often rely on targeted enforcement operations to disrupt spatial concentrations of activity. However, a central concern in the literature is whether such interventions reduce activity overall or merely displace it geographically (the "balloon effect").

This paper evaluates the spatial and causal effects of a targeted intervention using high-resolution geospatial data and panel econometric techniques.

---

## 2. Data and Spatial Construction

We use georeferenced event data aggregated at the H3 hexagonal grid level. The unit of analysis is:

H3 cell × day

We construct:

- Event counts per cell-day
- Treatment indicator based on pre-intervention intensity (top 10% cells)
- Post-intervention dummy
- Radial distance bands from the intervention epicenter

---

## 3. Empirical Strategy

### 3.1 Difference-in-Differences (Two-Way Fixed Effects)

We estimate:

Y_it = α_i + γ_t + β (Treat_i × Post_t) + ε_it

Where:

- α_i: cell fixed effects  
- γ_t: day fixed effects  
- Errors clustered at the cell level  

### 3.2 Event Study

We estimate dynamic treatment effects relative to the intervention date to test for pre-trends and dynamic responses.

### 3.3 Radial Spillover Model

We estimate distance-based treatment effects using concentric rings (0–500m, 500–1000m, 1000–1500m) to detect displacement patterns.

---

## 4. Results

### 4.1 Main DiD Estimate

Treat × Post coefficient:

−1.67 events per cell-day (p < 0.001)

This indicates a statistically significant reduction in treated cells after the intervention.

### 4.2 Dynamic Effects

Pre-intervention coefficients remain close to zero, supporting the parallel trends assumption. Post-intervention effects show sustained reductions.

![Event Study Dynamic Effects](../reports/figures/event_study_did.png)

Figure 1. Event-study estimates relative to the intervention date. 
Pre-intervention coefficients remain statistically indistinguishable from zero, supporting the parallel trends assumption.

### 4.3 Radial Spillover

---

## 5. Discussion

Results suggest that targeted enforcement reduces local intensity and exhibits spatial decay rather than pure displacement in the synthetic scenario. The methodology demonstrates how spatial panel econometrics can support evidence-based policy evaluation.

---

## 6. Conclusion

Combining hexagonal spatial aggregation, causal panel models, and spillover analysis provides a rigorous framework for evaluating territorial security policies. Future applications using administrative data can inform integrated public policy design.

