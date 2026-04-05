!pip install -U scikit-fuzzy  # Jalankan ini jika di Colab belum terinstall

import pandas as pd
import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc, brier_score_loss
import gc

# ============================================================
# 1. LOAD DATASET MINI
# ============================================================
path = '/content/VLIF_50000_SAMPLES.csv'
df = pd.read_csv(path)

# Persiapkan data untuk skfuzzy
data_input = df[['vpd_norm', 'lvi_norm']].values.T

# ============================================================
# 2. RUN FUZZY C-MEANS (K=3)
# ============================================================
cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(
    data_input, c=3, m=2, error=0.005, maxiter=1000, init=None
)

# ============================================================
# 3. LABELING & SORTING
# ============================================================
cluster_priority = np.sum(cntr, axis=1).argsort()
low_idx, mod_idx, high_idx = cluster_priority[0], cluster_priority[1], cluster_priority[2]

df['prob_low'] = u[low_idx]
df['prob_moderate'] = u[mod_idx]
df['prob_high'] = u[high_idx]

df['risk_cluster'] = np.argmax(u, axis=0)
label_map = {low_idx: 0, mod_idx: 1, high_idx: 2}
df['risk_cluster'] = df['risk_cluster'].map(label_map)

# ============================================================
# 4. HITUNG METRIK VALIDASI & STATISTIK KLASTER
# ============================================================
y_true = (df['jumlah_hotspot'] > 0).astype(int)
y_score = df['prob_high'] 

# Metrik Validasi
fpr, tpr, _ = roc_curve(y_true, y_score)
roc_auc = auc(fpr, tpr)
brier = brier_score_loss(y_true, y_score)

# Statistik Distribusi & Efektivitas per Klaster
total_samples = len(df)
total_hotspots = df['jumlah_hotspot'].sum()
total_frp = df['frp'].sum()

stats = []
for i, label in enumerate(['LOW', 'MODERATE', 'HIGH']):
    mask = df['risk_cluster'] == i
    area_pct = (mask.sum() / total_samples) * 100
    h_count = df.loc[mask, 'jumlah_hotspot'].sum()
    h_pct = (h_count / total_hotspots * 100) if total_hotspots > 0 else 0
    f_sum = df.loc[mask, 'frp'].sum()
    f_pct = (f_sum / total_frp * 100) if total_frp > 0 else 0
    stats.append([label, area_pct, h_count, h_pct, f_sum, f_pct])

# ============================================================
# 5. VISUALISASI GRAFIK ROC
# ============================================================
plt.figure(figsize=(10, 5), dpi=150)
plt.plot(fpr, tpr, color='#c0392b', lw=3, label=f'VLIF-Model (AUC = {roc_auc:.4f})')
plt.plot([0, 1], [0, 1], color='#2c3e50', lw=1.5, linestyle='--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Validation: ROC Curve')
plt.legend(loc="lower right")
plt.grid(True, alpha=0.3)
plt.show()

# ============================================================
# 6. TABEL OUTPUT LENGKAP
# ============================================================
print("\n" + "="*85)
print(f"{'STATISTIK DISTRIBUSI & VALIDASI KLASTER VLIF-MODEL':^85}")
print("="*85)
print(f"{'Risk Class':<12} | {'% Area':<10} | {'Hotspots':<10} | {'% Hotspot':<10} | {'Total FRP':<12} | {'% FRP':<8}")
print("-" * 85)
for s in stats:
    print(f"{s[0]:<12} | {s[1]:>9.2f}% | {s[2]:>10.0f} | {s[3]:>9.2f}% | {s[4]:>12.2f} | {s[5]:>7.2f}%")
print("-" * 85)

print(f"\nVALIDATION SUMMARY:")
print(f"1. FPC (Structural Stability) : {fpc:.4f}")
print(f"2. ROC-AUC (Predictive Power) : {roc_auc:.4f}")
print(f"3. Brier Score (Accuracy)     : {brier:.4f}")
print(f"4. Total Hotspots Processed   : {total_hotspots:,.0f}")
print("="*85)

# ============================================================
# 7. EXPORT DATASET
# ============================================================
df.to_csv('/content/VLIF_CLUSTER_RESULT_TEST.csv', index=False)
print(f"\n✅ Dataset berhasil disimpan ke /content/VLIF_CLUSTER_RESULT_TEST.csv")
