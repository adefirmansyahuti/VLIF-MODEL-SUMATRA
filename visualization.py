# -*- coding: utf-8 -*-
"""
Visualization Script: VLIF Model Sumatra - Ujicoba GitHub
Periode: Triwulan 3 2025
"""

import os
import gc
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
import skfuzzy as fuzz
import numpy as np

# ============================================================
# 1. KONFIGURASI PATH & LOADING DATA
# ============================================================
path_csv = '/content/DATASET_GITHUB_SUMATRA_Q3_2025.csv'
path_geojson = '/content/gabungan_10_wilayah_batas_provinsi.geojson'
output_peta = '/content/PETA_Q3_2025_FINAL.png'

# Validasi Keberadaan File
if not os.path.exists(path_csv) or not os.path.exists(path_geojson):
    raise FileNotFoundError("❌ Pastikan file CSV dan GeoJSON sudah ada di path yang benar!")

df = pd.read_csv(path_csv)

# Filter 8 Provinsi Utama (Pembersihan Data)
list_hapus = ['KEPULAUAN RIAU', 'BANGKA BELITUNG', 'KEPULAUAN BANGKA BELITUNG', 'KEPRI', 'BABEL']
df = df[~df['provinsi'].str.upper().isin(list_hapus)]

# ============================================================
# 2. RE-RUN CLUSTERING (IN MEMORY)
# ============================================================
def run_ufcm_for_viz(data):
    """Fungsi clustering Fuzzy C-Means dalam memori."""
    X = data.reshape(1, -1)
    cntr, u, _, _, _, _, _ = fuzz.cluster.cmeans(
        X, c=3, m=2.0, error=1e-5, maxiter=1000, init=None
    )
    # Sorting Cluster agar 0=Aman(Low), 1=Waspada(Mod), 2=Awas(High)
    idx = np.argsort(cntr.flatten())
    labels = np.argmax(u[idx], axis=0)
    cluster_map = {0: 'Aman', 1: 'Waspada', 2: 'Awas'}
    return [cluster_map[l] for l in labels]

if 'FLFI' in df.columns:
    df['klaster_risiko_fcm'] = run_ufcm_for_viz(df['FLFI'].values)
else:
    raise KeyError("❌ Error: Kolom 'FLFI' tidak ditemukan di dataset!")

# ============================================================
# 3. KALKULASI FLF RISK SCORE (FLFRS) & STATUS
# ============================================================
stats = df.groupby(['provinsi', 'klaster_risiko_fcm']).size().unstack(fill_value=0)
stats_pct = (stats.divide(stats.sum(axis=1), axis=0) * 100)

total_hotspot = df['jumlah_hotspot'].sum()
total_grid = len(df)

def calculate_local_er(status):
    subset = df[df['klaster_risiko_fcm'] == status]
    if len(subset) == 0 or total_hotspot == 0: return 0
    hotspots_status = subset['jumlah_hotspot'].sum()
    grids_status = len(subset)
    er = (hotspots_status / total_hotspot) / (grids_status / total_grid)
    return er

ER_AWAS_Q3 = calculate_local_er('Awas')
ER_WASPADA_Q3 = calculate_local_er('Waspada')
ER_AMAN_Q3 = calculate_local_er('Aman')

# Hitung Skor FLFRS
stats_pct['FLFRS'] = (
    (stats_pct.get('Awas', 0) * ER_AWAS_Q3) +
    (stats_pct.get('Waspada', 0) * ER_WASPADA_Q3) +
    (stats_pct.get('Aman', 0) * ER_AMAN_Q3)
) / ER_AWAS_Q3

stats_pct = stats_pct.reset_index()

# Penentuan Status Final (Threshold: 25 & 50)
def mapping_status_final(flfrs):
    if flfrs > 50:   return 2   # AWAS (MERAH)
    if flfrs >= 25:  return 1   # WASPADA (KUNING)
    return 0                    # AMAN (HIJAU)

stats_pct['status_id'] = stats_pct['FLFRS'].apply(mapping_status_final)
stats_pct['join_key'] = stats_pct['provinsi'].str.upper().str.strip()

# ============================================================
# 4. PREPARASI DATA GEOSPATIAL
# ============================================================
gdf_final = gpd.read_file(path_geojson)
gdf_final['join_key'] = gdf_final['name'].str.upper().str.strip()
gdf_final = gdf_final[~gdf_final['join_key'].isin(list_hapus)]

# Merge Data Statistik ke GeoDataFrame
merged = gdf_final.merge(stats_pct, on='join_key', how='left').fillna(0)

# ============================================================
# 5. VISUALISASI PETA (LAYOUT CENTERED)
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(25, 25), facecolor='white')

# Definisi Colormap (Hijau -> Kuning -> Merah)
cmap_manjur = ListedColormap(['#2ecc71', '#f1c40f', '#e74c3c'])

# Mapping Nama Provinsi untuk Label (Singkat)
short_name = {
    'SUMATERA UTARA': 'SUMUT', 'SUMATERA SELATAN': 'SUMSEL',
    'SUMATERA BARAT': 'SUMBAR', 'RIAU': 'RIAU', 'JAMBI': 'JAMBI',
    'ACEH': 'ACEH', 'BENGKULU': 'BENGKULU', 'LAMPUNG': 'LAMPUNG'
}

# Plot Peta Dasar
merged.plot(column='status_id', ax=ax, cmap=cmap_manjur, vmin=0, vmax=2,
            edgecolor='#2c3e50', linewidth=2, zorder=3)

# Penambahan Label pada Centroid Provinsi
for idx, row in merged.iterrows():
    if row['geometry'] is not None:
        centroid = row['geometry'].centroid
        lbl = short_name.get(row['join_key'], row['join_key'])
        
        # Penyesuaian posisi teks manual agar tidak tumpang tindih
        offsets = {
            'SUMATERA BARAT': (0.1, -0.2),
            'RIAU': (0.1, 0.2),
            'JAMBI': (-0.1, 0.1),
            'SUMATERA SELATAN': (0.0, 0.1),
            'LAMPUNG': (0.0, 0.2),
            'ACEH': (0.0, -0.3)
        }
        off_x, off_y = offsets.get(row['join_key'], (0.0, 0.0))
        
        val_text = f"{lbl}\n{row['FLFRS']:.1f}"

        ax.text(centroid.x + off_x, centroid.y + off_y, val_text,
                fontsize=20, fontweight='black', ha='center', va='center',
                color='black', zorder=10,
                path_effects=[path_effects.withStroke(linewidth=10, foreground='white')])

# Pengaturan Batas Pandang (Zoom to Sumatera)
bounds = gdf_final.total_bounds
ax.set_xlim(bounds[0]-0.5, bounds[2]+0.5)
ax.set_ylim(bounds[1]-0.5, bounds[3]+0.5)

# --- PRESISI TATA LETAK JUDUL (DIGABUNG) ---
ax.axis('off')

# Judul Utama dan Sub-judul (Triwulan) digabung jadi 1 kesatuan
combined_title = ('MONITORING THE RISK STATUS OF SUMATERA FOREST AND LAND FIRE \n'
                  '(8 MAIN LAND PROVINCES) - BASE ON FLFRS, SCALE 0–100\n'
                  'TRIWULAN 3 - 2025')

plt.suptitle(combined_title,
             fontsize=35, fontweight='black', y=0.98, ha='center')

# ============================================================
# 6. LEGENDA & TATA LETAK (CENTERED)
# ============================================================
# Membuat Patch Legenda
leg_patches = [
    mpatches.Patch(color='#e74c3c', label='HIGH RISK (FLFRS > 50)'),
    mpatches.Patch(color='#f1c40f', label='MODERATE RISK (FLFRS 25–50)'),
    mpatches.Patch(color='#2ecc71', label='LOW RISK (FLFRS < 25)')
]

# Legenda di luar area plot utama
ax.legend(handles=leg_patches, loc='center left', bbox_to_anchor=(1.05, 0.5),
          fontsize=20, frameon=True, shadow=True, facecolor='white',
          title=f"FLFRS THRESHOLD\n(LOCAL ER Q3)", title_fontsize=22)

# --- FINAL ADJUSTMENT FOR PADDING ---
plt.subplots_adjust(right=0.75, top=0.90, bottom=0.05) # Mengatur ruang agar tidak dempet
plt.savefig(output_peta, dpi=300, bbox_inches='tight')
plt.show()

# Membersihkan memori
gc.collect()
