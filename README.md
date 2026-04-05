# Spatio-Temporal Forest and Land Fire Risk Modeling in Sumatra

Official implementation of the **VLIF-Model** (Vapor Pressure Deficit - Land Vulnerability Integrated Fuzzy Model), as presented in the research: *"Spatio-Temporal Forest and Land Fire Risk Modeling in Sumatra Using Atmospheric-Edaphic Integration via Bivariate Fuzzy C-Means"*.

## 📌 Overview
The VLIF-Model integrates atmospheric water demand (VPD) and edaphic (soil) vulnerability (LVI) to map vegetation fire risks. This model objectively zones fire risks using **Bivariate Fuzzy C-Means (FCM)**. 

This repository contains the analytical scripts and a representative dataset (50,000 samples) covering the **2023–2024** El Niño period in Sumatra, enabling full reproducibility of the clustering and geospatial visualization processes.

## 🚀 Performance Metrics (Revisi 2026 Validation)
Based on the spatial model validation using ground truth VIIRS thermal anomalies (hotspots):

| Metric | Value | Interpretation |
| :--- | :--- | :--- |
| **ROC-AUC** | **0.7797** | Strong predictive power in distinguishing fire occurrence. |
| **FPC** (Fuzzy Partition Coefficient) | **0.6149** | High structural stability for K=3 clustering. |
| **Brier Score** | **0.0956** | High accuracy of the probabilistic risk forecast. |

### 📊 Cluster Distribution & Effectiveness
The model demonstrates exceptional spatial efficiency, specifically in the **High-Risk** zone:

| Risk Class | % Area | % Hotspot Captured | % Total FRP (Energy) |
| :--- | :--- | :--- | :--- |
| **LOW** | 41.31% | 5.56% | 3.85% |
| **MODERATE** | 41.41% | 12.91% | 10.00% |
| **HIGH** | **17.28%** | **81.54%** | **86.14%** |

> **Key Finding:** The **High-Risk** cluster covers only **~17%** of the total study area but successfully identifies over **81%** of fire hotspots and **86%** of the total Fire Radiative Power (FRP), proving high precision in spatial filtering.

## 📁 Repository Structure
* `main.py`: Core logic for Bivariate FCM clustering, automatic label sorting, and validation metrics calculation. Exports processed data to `VLIF_CLUSTER_RESULT_TEST.csv`.
* `visualization.py`: Script for spatial quarterly modal aggregation, grid interpolation, and generating the 4-panel Quarterly Risk Map.
* `VLIF_50000_SAMPLES.csv`: Compiled dataset (VPD, LVI, Hotspots, FRP).
* `provinsisumatera.geojson`: Sumatra provincial boundaries for mapping.

## 🗺️ Visualization Result (Quarter 1-4)
![Sumatra VLIF-Model Fire Risk Map](risk_map_vlif_model.png)
*Figure: Spatio-temporal distribution of forest fire risk in Sumatra (Quarter 1-4) using the VLIF-Model.*

## 📜 Methodology
1.  **Data Preprocessing**: Normalization of bivariate inputs (`vpd_norm` and `lvi_norm`).
2.  **Clustering (Bivariate FCM)**: Dynamic classification into Low, Moderate, and High Risk zones.
3.  **Validation**: Evaluating model precision using ROC-AUC and energy-based (FRP) cluster statistics.
4.  **Geospatial Mapping**: Aggregating risk classes into Quarterly Modals and applying spatial interpolation.

## 🛠️ Installation & Execution
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run clustering and validation
python main.py

# 3. Render and display the map
python visualization.py
