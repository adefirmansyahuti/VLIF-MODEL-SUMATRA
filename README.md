# Spatio-Temporal Forest and Land Fire Risk Modeling in Sumatra

Official implementation of the **VLIF-Model** (Vapor Pressure Deficit - Land Vulnerability Integrated Fuzzy Model), as presented in the research: *"Spatio-Temporal Forest and Land Fire Risk Modeling in Sumatra Using Atmospheric-Edaphic Integration via Univariate Fuzzy C-Means"*.

## 📌 Overview
The VLIF-Model integrates atmospheric water demand (VPD) and edaphic vulnerability (LVI/IBK) into a single physical index called **FLFI** (Forest and Land Fire Index). This model objectively zones fire risks using **Univariate Fuzzy C-Means (U-FCM)** and provides a regional risk metric called **FLFRS** (FLF Risk Score).

## 🚀 Key Performance (Q3 2025)
Based on validation using real-time hotspot data from Sumatra (July–September 2025):
* **High-Risk Efficiency Ratio (ER): 3.14** (Meaning the model is 3.14x more effective at identifying fire locations compared to random spatial distribution).
* **Objective Zoning**: Successfully classifies Sumatra into three risk levels: Low (Aman), Moderate (Waspada), and High (Awas).

## 📁 Repository Structure
* `main.py`: Core logic for FLFI calculation, U-FCM clustering, and Efficiency Ratio (ER) validation.
* `visualization.py`: Script for regional risk extraction (FLFRS) and geospatial mapping.
* `DATASET_GITHUB_SUMATRA_Q3_2025.csv`: Compiled spatio-temporal dataset.
* `gabungan_10_wilayah_batas_provinsi.geojson`: Sumatra administrative boundaries for mapping.
* `requirements.txt`: List of required Python libraries.

## 📊 Dataset Features
| Feature | Description |
| :--- | :--- |
| `flfi_generated` | Integrated Fire Risk Index (Atmospheric + Edaphic) |
| `status_id` | Risk Cluster (0: Low, 1: Moderate, 2: High) |
| `FLFRS` | Regional Risk Score (Scale 0-100) used for the map |
| `jumlah_hotspot` | Ground truth data (Target Variable) |

## 🗺️ Visualization Result
![Sumatra Fire Risk Map](RISK_MAP_FLFRS_FINAL.png)

## 🛠️ Installation
```bash
pip install -r requirements.txt
python main.py
python visualization.py