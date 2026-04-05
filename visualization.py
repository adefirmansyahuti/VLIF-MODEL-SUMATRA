import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
import geopandas as gpd
from scipy.interpolate import griddata
from matplotlib.colors import ListedColormap, BoundaryNorm
import gc

# ============================================================
# 1. DEFINISI FUNGSI INTERPOLASI & MODUS
# ============================================================
def get_grid_bivariat(df_q, polygon_mask):
    minx, miny, maxx, maxy = polygon_mask.bounds
    # Grid 500x500 untuk kehalusan visual
    grid_x, grid_y = np.mgrid[minx:maxx:500j, miny:maxy:500j]

    points = df_q[['longitude', 'latitude']].values
    values = df_q['risk_cluster'].values

    # Interpolasi Linear untuk transisi warna yang halus
    grid_z = griddata(points, values, (grid_x, grid_y), method='linear')

    # Masking agar hanya muncul di daratan Sumatra (sesuai GeoJSON)
    from shapely.vectorized import contains
    mask = contains(polygon_mask, grid_x, grid_y)
    grid_z[~mask] = np.nan

    return grid_x, grid_y, grid_z

def get_mode(x):
    m = x.mode()
    return m.iloc[0] if not m.empty else np.nan

# ============================================================
# 2. SETUP WARNA (HIJAU - KUNING - MERAH)
# ============================================================
cmap_v9 = ListedColormap(['#8DB600', '#FFFF00', '#FF0000'])
norm_v9 = BoundaryNorm([-0.5, 0.5, 1.5, 2.5], cmap_v9.N)

# ============================================================
# 3. LOAD DATA HASIL CLUSTERING & GEOJSON
# ============================================================
path_csv = "/content/VLIF_CLUSTER_RESULT_TEST.csv"  # SESUAI DATASET BARU
path_geojson = "/content/provinsisumatera.geojson"

df = pd.read_csv(path_csv)
df['date'] = pd.to_datetime(df['date'])
df['triwulan'] = df['date'].dt.quarter

gdf = gpd.read_file(path_geojson)
gdf['name'] = gdf['name'].str.upper().str.strip()

prov_map = {
    'ACEH': 1, 'SUMATERA UTARA': 2, 'SUMATERA BARAT': 3, 'RIAU': 4,
    'JAMBI': 5, 'SUMATERA SELATAN': 6, 'BENGKULU': 7, 'LAMPUNG': 8
}

gdf_sumatra = gdf[gdf['name'].isin(prov_map.keys())].copy()
gdf_sumatra['prov_id'] = gdf_sumatra['name'].map(prov_map)
sumatra_union = gdf_sumatra.union_all()

# Agregasi Spasial per Grid (Round 2 digit) untuk efisiensi visualisasi
temp_agg = df.assign(
    lat_round=df['latitude'].round(2),
    lon_round=df['longitude'].round(2)
).groupby(['lon_round', 'lat_round', 'triwulan'])['risk_cluster'].agg(get_mode).reset_index()
temp_agg.columns = ['longitude', 'latitude', 'triwulan', 'risk_cluster']

# ============================================================
# 4. PLOTTING (QUARTER 1-4)
# ============================================================
fig, axes = plt.subplots(1, 4, figsize=(52, 21), facecolor='white')
plt.subplots_adjust(left=0.05, right=0.95, top=0.88, bottom=0.18, wspace=0.01)

for i, q in enumerate([1, 2, 3, 4]):
    ax = axes[i]
    df_q = temp_agg[temp_agg['triwulan'] == q].copy()

    if not df_q.empty:
        # Layer 1: Background Daratan
        gdf_sumatra.plot(ax=ax, facecolor='#F7FDF7', edgecolor='none', zorder=0)

        # Layer 2: Interpolasi Risiko (VLIF-Model)
        gx, gy, z_final = get_grid_bivariat(df_q, sumatra_union)
        im = ax.pcolormesh(gx, gy, z_final, cmap=cmap_v9, norm=norm_v9,
                           shading='nearest', zorder=1, alpha=0.9)

        # Layer 3: Border Provinsi
        gdf_sumatra.plot(ax=ax, facecolor='none', edgecolor='#000000', linewidth=3.5, zorder=10)

        # Layer 4: Indeks Angka Provinsi
        for _, row in gdf_sumatra.iterrows():
            coords = row.geometry.representative_point().coords[0]
            txt = ax.text(coords[0], coords[1], str(int(row['prov_id'])),
                          fontsize=45, fontweight='black', color='black',
                          ha='center', va='center', zorder=100)
            txt.set_path_effects([PathEffects.withStroke(linewidth=5, foreground='white')])

    ax.set_xlim(94.8, 106.3)
    ax.set_ylim(-6.0, 5.9)
    ax.set_title(f'QUARTER {q}', fontsize=65, fontweight='black', pad=25)
    ax.axis('off')

# Footer: Legenda Nama Provinsi
h_legend = "  |  ".join([f"{v}. {k}" for k, v in prov_map.items()])
fig.text(0.5, 0.12, h_legend, ha='center', fontsize=40, fontweight='bold', family='monospace')

# Footer: Legenda Tingkat Risiko
cbar_ax = fig.add_axes([0.35, 0.08, 0.3, 0.012])
cbar = fig.colorbar(im, cax=cbar_ax, orientation='horizontal', ticks=[0, 1, 2])
cbar.ax.set_xticklabels(['LOW RISK', 'MODERATE RISK', 'HIGH RISK'], fontsize=32, fontweight='bold')

# Header Utama
fig.text(0.5, 0.94, 'SUMATRA ISLAND VLIF-MODEL FIRE RISK (SPATIAL QUARTERLY MODAL)',
         ha='center', fontsize=65, fontweight='black')

plt.show()

# Cleanup RAM
del temp_agg
gc.collect()
