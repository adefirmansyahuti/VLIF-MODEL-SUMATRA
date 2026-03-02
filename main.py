# -*- coding: utf-8 -*-
"""
Main Script: VLIF Model Sumatra - Ujicoba GitHub (Full Validation - In Memory)
"""

import os
import sys

# --- AUTO-INSTALLER ---
try:
    import numpy as np
    import pandas as pd
    import skfuzzy as fuzz
    from scipy.stats import pearsonr
except ImportError:
    print("Installing required libraries... please wait.")
    os.system(f"{sys.executable} -m pip install numpy pandas scikit-fuzzy scipy")
    import numpy as np
    import pandas as pd
    import skfuzzy as fuzz
    from scipy.stats import pearsonr

# ==========================================
# VLIF MODEL (INTEGRATION VPD + IBK/LVI)
# ==========================================
class VLIFModelSumatra:
    def __init__(self, m=2.0, epsilon=1e-5, max_iter=1000):
        self.m = m
        self.epsilon = epsilon
        self.max_iter = max_iter
        self.centroids = None
        self.fpc = None # Fuzzy Partition Coefficient

    def run_ufcm(self, data):
        X = data.reshape(1, -1)
        cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(
            X, c=3, m=self.m, error=self.epsilon,
            maxiter=self.max_iter, init=None
        )
        self.fpc = fpc # Spatial Separation Metric
        
        # Sorting Clusters: 0=Aman(Low), 1=Waspada(Mod), 2=Awas(High)
        idx = np.argsort(cntr.flatten())
        self.centroids = cntr[idx]
        return np.argmax(u[idx], axis=0)

    # 1. METRIC: EFFICIENCY RATIO (ER)
    def validate_er(self, df, label_col, hotspot_col):
        total_h = df[hotspot_col].sum()
        total_n = len(df)
        results = []
        labels = {0: 'Low Risk', 1: 'Moderate Risk', 2: 'High Risk'}

        for i in range(3):
            subset = df[df[label_col] == i]
            n_i = len(subset)
            h_i = subset[hotspot_col].sum()
            er = (h_i / total_h) / (n_i / total_n) if total_h > 0 else 0
            results.append({'Cluster': labels[i], 'Hotspots': h_i, 'Area_Size': n_i, 'ER': round(er, 4)})
        return pd.DataFrame(results)

    # 2. METRIC: EFFECT SIZE (COHEN'S D)
    def calculate_cohens_d(self, df, value_col, label_col):
        high_risk = df[df[label_col] == 2][value_col]
        low_risk = df[df[label_col] == 0][value_col]
        
        n1, n2 = len(high_risk), len(low_risk)
        var1, var2 = high_risk.var(), low_risk.var()
        
        # Pooled standard deviation
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        d = (high_risk.mean() - low_risk.mean()) / pooled_std
        return d

    # 3. METRIC: MONTHLY R-SQUARED
    def calculate_monthly_r2(self, df, value_col, hotspot_col, date_col):
        df[date_col] = pd.to_datetime(df[date_col])
        df['month'] = df[date_col].dt.to_period('M')
        
        monthly_data = df.groupby('month').agg({
            value_col: 'mean',
            hotspot_col: 'sum'
        })
        
        r, _ = pearsonr(monthly_data[value_col], monthly_data[hotspot_col])
        return r**2

if __name__ == "__main__":
    file_path = '/content/DATASET_GITHUB_SUMATRA_Q3_2025.csv'

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        model = VLIFModelSumatra()

        if 'FLFI' in df.columns:
            print(f"Processing Dataset (In-Memory): {file_path}")
            
            # --- CLUSTERING IN MEMORY ONLY ---
            # Original CSV data will NOT be modified
            df_temp = df.copy()
            df_temp['Risk_Status'] = model.run_ufcm(df_temp['FLFI'].values)

            # --- FULL VALIDATION ---
            print("\nVLIF-MODEL VALIDATION METRICS (Using Existed FLFI)")
            print("="*65)
            
            # A. Efficiency Ratio
            print("\n[1] Cluster Efficiency Ratio (ER):")
            report = model.validate_er(df_temp, 'Risk_Status', 'jumlah_hotspot')
            print(report.to_string(index=False))
            
            # B. Spatial Separation (FPC)
            print(f"\n[2] Spatial Separation (Fuzzy Partition Coeff - FPC): {model.fpc:.4f}")
            
            # C. Predictive Power (Cohen's d)
            cohen_d = model.calculate_cohens_d(df_temp, 'FLFI', 'Risk_Status')
            print(f"[3] Predictive Power (Cohen's d): {cohen_d:.4f}")
            
            # D. Monthly R-squared
            r2 = model.calculate_monthly_r2(df_temp, 'FLFI', 'jumlah_hotspot', 'tanggal_pengamatan')
            print(f"[4] Monthly Aggregated R-squared (R²): {r2:.4f}")
            print("="*65)
            
        else:
            print(f"❌ Error: Column 'FLFI' not found in {file_path}")
    else:
        print(f"❌ Error: File {file_path} not found!")
