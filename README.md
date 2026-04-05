# Spatio-Temporal Forest and Land Fire Risk Modeling in Sumatra

Official implementation of the **VLIF-Model** (Vapor Pressure Deficit - Land Vulnerability Integrated Fuzzy Model), as presented in the research: *"Spatio-Temporal Forest and Land Fire Risk Modeling in Sumatra Using Atmospheric-Edaphic Integration via Bivariate Fuzzy C-Means"*.

## 📌 Overview
The VLIF-Model integrates atmospheric water demand (VPD) and edaphic (soil) vulnerability (LVI) to map vegetation fire risks. This model objectively zones fire risks using **Bivariate Fuzzy C-Means (FCM)**. 

This repository contains the analytical scripts and a representative dataset (50,000 samples) covering the **2023–2024** El Niño period in Sumatra, enabling full reproducibility of the clustering and geospatial visualization processes.

## 🚀 Performance Metrics (Revisi 2026 Validation)
Based on the spatial model validation using ground truth VIIRS thermal anomalies (hotspots):

| Metric | Value | Interpretation |
| :--- | :--- | :--- |
| **ROC-AUC** | **0.8288** | Excellent predictive power in distinguishing fire occurrence. |
| **FPC** (Fuzzy Partition Coefficient) | **0.6137** | High structural stability for K=3 clustering. |
| **Brier Score** | **0.0956** | High accuracy of the probabilistic risk forecast. |

### 📊 Cluster Distribution & Effectiveness
The model demonstrates exceptional spatial efficiency, specifically in the **High-Risk** zone:

| Risk Class | % Area | % Hotspot Captured | % Total FRP (Energy) |
| :--- | :--- | :--- | :--- |
| **LOW** | 41.31% | 5.56% | 3.85% |
| **MODERATE** | 41.41% | 12.91% | 10.00% |
| **HIGH** | **17.28%** | **81.54%** | **86.14%** |

> **Key Finding:** The **High-Risk** cluster covers only **~17%** of the total study area but successfully identifies over **81%** of fire hotspots and **86%** of the total Fire Radiative Power (FRP).

## 📂 Data Acquisition & Sources
This study utilizes an integrated dataset of 2,614,056 spatial observations. Key data sources include:
1. **Hotspots (Ground Truth):** S-NPP VIIRS (375m) from NASA FIRMS portal.
2. **Meteorology & Soil:** ECMWF ERA5-Land (Temperature, RH, Soil Moisture).
3. **Land Cover:** MODIS MCD12Q1 (v6.1) global classification at 500m resolution.
4. **Peatland:** Global Forest Watch (GFW) Indonesian peatland map.
5. **Anthropogenic Markers:** OpenStreetMap (OSM) extracts via Geofabrik (Roads & Settlements).
6. **Administrative Boundaries:** GeoJSON boundaries based on Indonesian Ministry of Home Affairs Decree (2025).

## 🛠️ Data Pipeline & Integration (Optional)
You can replicate the dataset construction from scratch using the provided pipeline.

* **Pipeline Script**: `vlif_dataset_integration.py`
* **Large File Download**: Due to GitHub size limits, the **Human_Activity_Index.zip** (containing OSM infrastructure data) must be downloaded from the following link:
  > [🔗 Download Human_Activity_Index.zip https://bit.ly/HumanActivityZipFile

> [!IMPORTANT]
> **Technical Note on Dataset Population:**
> The provided `VLIF_50000_SAMPLES.csv` is a statistically preserved sample derived from the original research population of **2,614,056 observations**. 
> 
> This full population represents a complete 2-year spatio-temporal grid (January 2023 – December 2024) covering the entire Sumatra region, with a spatial resolution of **0.1° (~11.1 km per grid)**. 
> 
> If you choose to re-run the `vlif_dataset_integration.py` script using only the provided 50k sample framework, the resulting normalization values (`vpd_norm`, `lvi_norm`) will differ slightly. This is because the global normalization in the official dataset was calculated based on the maximum and minimum values of the entire 2.6 million-row population to ensure regional consistency. However, the core research substance, model logic, and risk patterns remain identical.

## 📁 Repository Structure
* `vlif_dataset_integration.py`: Script to fuse multi-source raw data into the integrated VLIF format.
* `main.py`: Core logic for Bivariate FCM clustering, automatic label sorting, and validation.
* `visualization.py`: Script for spatial quarterly modal aggregation and risk map rendering.
* `VLIF_50000_SAMPLES.csv`: Official representative dataset (Sampled from 2.6M records).
* `provinsisumatera.geojson`: Sumatra provincial boundaries.

## 🗺️ Visualization Result (Quarter 1-4)
![Sumatra VLIF-Model Fire Risk Map](risk_map_vlif_model.png)
*Figure: Spatio-temporal distribution of forest fire risk in Sumatra (Quarter 1-4) using the VLIF-Model.*

## 📜 Methodology
1. **Data Integration**: Fusing atmospheric (VPD), edaphic (Peat & Land Cover), and anthropogenic (HAI) data.
2. **Preprocessing**: Global normalization of bivariate inputs (`vpd_norm` and `lvi_norm`).
3. **Clustering (Bivariate FCM)**: Dynamic classification into Low, Moderate, and High Risk zones.
4. **Validation**: Evaluating model precision using ROC-AUC and energy-based (FRP) statistics.
5. **Geospatial Mapping**: Aggregating risk classes into Quarterly Modals and spatial interpolation.

## ⚙️ Execution Guide

### Option 1: Quick Start (Ready-to-Use Dataset)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run clustering and validation
python main.py

# 3. Render and display the map
python visualization.py
