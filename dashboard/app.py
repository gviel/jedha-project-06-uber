"""app.py — Dashboard Streamlit : Uber NYC Hot-zones (septembre 2014).

Animation heure-par-heure via frames Plotly natives (slider + Play intégrés dans la carte).
Aucun st.rerun() — l'animation s'exécute côté client sans rechargement de page.

Lancement :
    conda activate uber
    streamlit run dashboard/app.py
"""
import os
from pathlib import Path

import h3
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from pyproj import Transformer
from sklearn.cluster import DBSCAN, HDBSCAN, KMeans

# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────
_LOCAL_DATA = Path(__file__).parent / "dashboard_sept2w.parquet"
_S3_DATA    = "s3://cdsd-uber-data/dashboard_sept2w.parquet"
NY_CENTER = dict(lat=40.7128, lon=-74.0060)
MAP_STYLE = "carto-positron"

DOW_LABELS = {1: "Lun", 2: "Mar", 3: "Mer", 4: "Jeu", 5: "Ven", 6: "Sam", 7: "Dim"}
DOW_PILLS  = [f"{v} ({k})" for k, v in DOW_LABELS.items()]

_TRANSFORMER = Transformer.from_crs("EPSG:4326", "EPSG:32618", always_xy=True)

st.set_page_config(page_title="Uber NYC Hot-zones", layout="wide", page_icon="🚖")

# ─────────────────────────────────────────────────────────────────────────────
# Données
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Chargement des données …")
def load_data() -> pd.DataFrame:
    if _LOCAL_DATA.exists():
        return pd.read_parquet(_LOCAL_DATA)
    # Production (Streamlit Cloud) : lecture depuis S3
    aws = st.secrets.get("aws", {})
    if aws:
        os.environ.setdefault("AWS_ACCESS_KEY_ID",     aws["access_key_id"])
        os.environ.setdefault("AWS_SECRET_ACCESS_KEY", aws["secret_access_key"])
        os.environ.setdefault("AWS_DEFAULT_REGION",    aws.get("region", "eu-west-3"))
    return pd.read_parquet(_S3_DATA)


df_all = load_data()

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def utm_xy(lon_arr, lat_arr) -> np.ndarray:
    x, y = _TRANSFORMER.transform(lon_arr, lat_arr)
    return np.column_stack([x, y])


def hour_df(dow: int, h: int) -> pd.DataFrame:
    return df_all[(df_all["dow"] == dow) & (df_all["hour"] == f"{h:02d}")]


def _animation_layout(speed_ms: int, h0: int = 16) -> dict:
    """Retourne sliders + updatemenus pour les figures animées (commun H3 et clustering)."""
    steps = [dict(
        method="animate",
        args=[[f"{h:02d}h"],
              dict(mode="immediate",
                   frame=dict(duration=speed_ms, redraw=True),
                   transition=dict(duration=0))],
        label=f"{h:02d}h",
    ) for h in range(24)]

    sliders = [dict(
        active=h0,
        steps=steps,
        currentvalue=dict(prefix="Heure : ", visible=True, font=dict(size=14)),
        pad=dict(t=55, b=10),
        len=0.82, x=0.12,
    )]

    updatemenus = [dict(
        type="buttons", showactive=False,
        x=0.01, y=0, xanchor="left", yanchor="top",
        buttons=[
            dict(label="▶",
                 method="animate",
                 args=[None, dict(frame=dict(duration=speed_ms, redraw=True),
                                 fromcurrent=True, transition=dict(duration=0))]),
            dict(label="⏸",
                 method="animate",
                 args=[[None], dict(mode="immediate", frame=dict(duration=0))]),
        ],
    )]
    return dict(sliders=sliders, updatemenus=updatemenus)


# ─────────────────────────────────────────────────────────────────────────────
# Builder H3 — pré-calcule 24 frames (mis en cache par paramètres)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Calcul H3 sur 24h …")
def build_h3_fig(dow: int, resolution: int, N: int, speed_ms: int) -> go.Figure:
    all_cells_set: set = set()
    hour_counts: dict = {}
    total_pts = 0

    # Échantillonnage proportionnel : chaque heure reçoit p_h × N points
    day_total = sum(len(hour_df(dow, h)) for h in range(24)) or 1

    for h in range(24):
        df_h = hour_df(dow, h)
        if df_h.empty:
            hour_counts[h] = {}
            continue
        n_h = max(1, round(len(df_h) / day_total * N))
        df_s = df_h.sample(min(n_h, len(df_h)), random_state=42).copy()
        total_pts += len(df_s)
        df_s["cell"] = df_s.apply(
            lambda r: h3.latlng_to_cell(r["lat"], r["lon"], resolution), axis=1
        )
        counts = df_s.groupby("cell").size().to_dict()
        hour_counts[h] = counts
        all_cells_set.update(counts.keys())

    all_cells = sorted(all_cells_set)
    if not all_cells:
        return go.Figure()

    # GeoJSON commun à tous les frames
    features = []
    for cell in all_cells:
        boundary = h3.cell_to_boundary(cell)
        coords = [[lon, lat] for lat, lon in boundary]
        coords.append(coords[0])
        features.append({"type": "Feature", "id": cell,
                         "geometry": {"type": "Polygon", "coordinates": [coords]}})
    geojson = {"type": "FeatureCollection", "features": features}

    zmax = max((v for hc in hour_counts.values() for v in hc.values()), default=1)

    def make_choropleth(h: int, show_colorbar: bool = False):
        z = [hour_counts[h].get(c, 0) for c in all_cells]
        return go.Choroplethmapbox(
            geojson=geojson, locations=all_cells, z=z,
            zmin=0, zmax=zmax,
            colorscale="YlOrRd", marker_opacity=0.7, marker_line_width=0,
            colorbar=dict(title="Pickups", thickness=12, len=0.45) if show_colorbar else None,
        )

    frames = [
        go.Frame(data=[make_choropleth(h)], name=f"{h:02d}h")
        for h in range(24)
    ]

    h0 = 16 if hour_counts.get(16) else next((h for h in range(24) if hour_counts.get(h)), 0)
    anim = _animation_layout(speed_ms, h0)

    _note = dict(text=f"{total_pts:,} / {N:,} points",
                 showarrow=False, x=0.01, y=0.01,
                 xref="paper", yref="paper",
                 xanchor="left", yanchor="bottom",
                 font=dict(size=11, color="#444"),
                 bgcolor="rgba(255,255,255,0.75)", borderpad=3)

    return go.Figure(
        data=[make_choropleth(h0, show_colorbar=True)],
        frames=frames,
        layout=go.Layout(
            mapbox=dict(style=MAP_STYLE, center=NY_CENTER, zoom=10),
            height=700,
            margin=dict(l=0, r=0, t=10, b=110),
            annotations=[_note],
            **anim,
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Builder Clustering — points + centroides, go.Scattermapbox, 1 trace/frame
# Tempo minimum 5 s (rendu WebGL + tuiles mapbox)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Clustering sur 24h …")
def build_cluster_fig(dow: int, algo: str, hour_threshold: int, metric: str, speed_ms: int,
                      eps: int = 100, min_s_db: int = 10,
                      min_cs: int = 50, min_s_hdb: int = 5,
                      method: str = "leaf", n_clusters: int = 20) -> go.Figure:

    hour_data: dict = {}
    global_max = 1
    total_pts = 0

    # Proportions par heure (heures avec ≥ 10 pickups bruts uniquement)
    hour_lens = {h: len(hour_df(dow, h)) for h in range(24)}
    day_total = sum(hour_lens.values()) or 1
    props = {h: v / day_total for h, v in hour_lens.items() if v >= 10}
    # N_carte garantit hour_threshold points pour l'heure la plus creuse
    p_min = min(props.values()) if props else 1.0
    N_carte = max(1, round(hour_threshold / p_min))

    for h in range(24):
        df_h = hour_df(dow, h)
        if h not in props:
            hour_data[h] = dict(lats=[NY_CENTER["lat"]], lons=[NY_CENTER["lon"]],
                                sizes=[0.01], colors=[0])
            continue

        n_h = max(1, round(props[h] * N_carte))
        df_s = df_h.sample(min(n_h, len(df_h)), random_state=42).copy()
        total_pts += len(df_s)
        X = utm_xy(df_s["lon"].values, df_s["lat"].values)

        if algo == "DBSCAN":
            labels = DBSCAN(eps=eps, min_samples=min_s_db,
                            metric=metric, n_jobs=-1).fit_predict(X)
        elif algo == "HDBSCAN":
            labels = HDBSCAN(min_cluster_size=min_cs, min_samples=min_s_hdb,
                             cluster_selection_method=method,
                             metric=metric, n_jobs=-1).fit_predict(X)
        else:  # KMeans
            labels = KMeans(n_clusters=n_clusters, random_state=42,
                            n_init="auto").fit_predict(X)

        df_s["cluster"] = labels
        df_clean = df_s[df_s["cluster"] >= 0].copy()
        if df_clean.empty:
            hour_data[h] = dict(lats=[NY_CENTER["lat"]], lons=[NY_CENTER["lon"]],
                                sizes=[0.01], colors=[0])
            continue

        grp = df_clean.groupby("cluster")
        c_sizes = grp.size()
        df_clean = df_clean.copy()
        df_clean["csize"] = df_clean["cluster"].map(c_sizes)
        global_max = max(global_max, int(df_clean["csize"].max()))

        # Points du cluster (petits)
        lats  = df_clean["lat"].tolist()
        lons  = df_clean["lon"].tolist()
        sizes = [4.0] * len(df_clean)
        colors = df_clean["csize"].tolist()

        # Centroides (grands, proportionnels à la taille du cluster)
        min_c   = int(c_sizes.min())
        range_c = int(c_sizes.max() - min_c) or 1
        centers = grp[["lat", "lon"]].mean()
        for ci in centers.index:
            cs = int(c_sizes[ci])
            lats.append(centers.loc[ci, "lat"])
            lons.append(centers.loc[ci, "lon"])
            sizes.append(15 + (cs - min_c) / range_c * 25)
            colors.append(cs)

        hour_data[h] = dict(lats=lats, lons=lons, sizes=sizes, colors=colors)

    def make_scatter(h: int) -> go.Scattermapbox:
        d = hour_data[h]
        return go.Scattermapbox(
            lat=d["lats"], lon=d["lons"],
            mode="markers",
            marker=dict(
                size=d["sizes"],
                color=d["colors"],
                colorscale="YlOrRd",
                cmin=0, cmax=global_max,
                opacity=0.7,
                sizemode="diameter",
                colorbar=dict(title="Pickups", thickness=12, len=0.45),
            ),
            hovertemplate="%{marker.color} pickups<extra></extra>",
        )

    frames = [go.Frame(data=[make_scatter(h)], name=f"{h:02d}h") for h in range(24)]
    h0 = 16
    _note = dict(text=f"{total_pts:,} pts · ≥{hour_threshold}/h (N_carte={N_carte:,})",
                 showarrow=False, x=0.01, y=0.01,
                 xref="paper", yref="paper",
                 xanchor="left", yanchor="bottom",
                 font=dict(size=11, color="#444"),
                 bgcolor="rgba(255,255,255,0.75)", borderpad=3)
    return go.Figure(
        data=[make_scatter(h0)],
        frames=frames,
        layout=go.Layout(
            mapbox=dict(style=MAP_STYLE, center=NY_CENTER, zoom=10),
            height=700,
            margin=dict(l=0, r=0, t=10, b=110),
            showlegend=False,
            annotations=[_note],
            **_animation_layout(speed_ms, h0),
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🚖 Uber NYC")
    st.caption("Hot-zones · Septembre 2014 (sem. 1–2)")
    st.divider()

    st.subheader("Filtres")

    selected_pill = st.pills(
        "Jour de semaine", options=DOW_PILLS, default="Jeu (4)",
        help="1 = Lundi … 7 = Dimanche",
    )
    if selected_pill is None:
        st.warning("Sélectionner un jour.")
        st.stop()
    selected_dow = int(selected_pill.split("(")[1].rstrip(")"))


# ─────────────────────────────────────────────────────────────────────────────
# Onglets
# ─────────────────────────────────────────────────────────────────────────────
dow_label = DOW_LABELS[selected_dow]
st.markdown(f"**{dow_label}**")

tab_h3, tab_kmeans, tab_dbscan, tab_hdbscan = st.tabs([
    "H3 — Binning hexagonal", "KMeans", "DBSCAN", "HDBSCAN"
])

# ═══════════════════════════════════════════════════════════════
# Onglet H3
# ═══════════════════════════════════════════════════════════════
with tab_h3:
    col_ctrl, col_map = st.columns([1, 3], gap="medium")

    with col_ctrl:
        st.subheader("Paramètres H3")
        resolution = st.slider(
            "Résolution", 6, 10, 8,
            help="6 ≈ 5 km²/hex · 7 ≈ 0,7 km²/hex · 8 ≈ 0,1 km²/hex · 9 ≈ 13 000 m²/hex",
        )
        st.caption(
            f"Résol. **{resolution}** ≈ "
            f"{['5 km²','0.7 km²','0.1 km²','13 000 m²','1 500 m²'][resolution-6]}/hex"
        )
        h3_speed = st.select_slider(
            "Tempo animation (s/heure)",
            options=[500, 1000, 1500, 2000, 3000],
            value=1500,
            format_func=lambda v: f"{v/1000:.1f} s/h",
        )
        N_SAMPLE = st.number_input(
            "Total points (journée)", min_value=200, max_value=50_000,
            value=24_000, step=500,
            help="Budget total de points pour la carte H3. Chaque heure reçoit une fraction proportionnelle à son volume de pickups.",
        )

    with col_map:
        fig_h3 = build_h3_fig(selected_dow, resolution, N_SAMPLE, h3_speed)
        st.plotly_chart(fig_h3, width='stretch')

# ═══════════════════════════════════════════════════════════════
# Onglet KMeans
# ═══════════════════════════════════════════════════════════════
with tab_kmeans:
    col_ctrl, col_map = st.columns([1, 3], gap="medium")

    with col_ctrl:
        st.subheader("Paramètres KMeans")
        km_k = st.slider(
            "Nombre de clusters (k)", 5, 50, 21,
            key="km_k",
            help="Nombre de hot-zones à identifier. Valeur du notebook : 21.",
        )
        km_threshold = st.slider(
            "Min points / heure", 200, 2000, 500, step=100,
            key="km_threshold",
            help="Seuil minimum garanti pour l'heure la plus creuse. Le budget total (N_carte) est calculé automatiquement.",
        )
        km_speed = st.select_slider(
            "Tempo animation (s/heure)",
            options=[5000, 6000, 8000, 10000],
            value=5000,
            key="km_speed",
            format_func=lambda v: f"{v//1000} s/h",
        )

    with col_map:
        fig_kmeans = build_cluster_fig(
            selected_dow, "KMeans", km_threshold, "euclidean", km_speed,
            n_clusters=km_k,
        )
        st.plotly_chart(fig_kmeans, width='stretch')

# ═══════════════════════════════════════════════════════════════
# Onglet DBSCAN
# ═══════════════════════════════════════════════════════════════
with tab_dbscan:
    col_ctrl, col_map = st.columns([1, 3], gap="medium")

    with col_ctrl:
        st.subheader("Paramètres DBSCAN")
        db_metric = st.selectbox(
            "Métrique de distance", ["manhattan", "euclidean"],
            key="db_metric",
            help="manhattan = adapté à la grille orthogonale des rues de NYC",
        )
        db_threshold = st.slider(
            "Min points / heure", 200, 2000, 500, step=100,
            key="db_threshold",
            help="Seuil minimum garanti pour l'heure la plus creuse. Le budget total (N_carte) est calculé automatiquement : N_carte = seuil / p_min.",
        )
        db_speed = st.select_slider(
            "Tempo animation (s/heure)",
            options=[5000, 6000, 8000, 10000],
            value=5000,
            key="db_speed",
            format_func=lambda v: f"{v//1000} s/h",
        )
        eps   = st.slider("eps (m)", 30, 500, 100, step=10,
                          key="db_eps",
                          help="~1 pâté de maisons NYC ≈ 80–120 m")
        db_mins = st.slider("min_samples", 3, 50, 10, key="db_mins")

    with col_map:
        fig_dbscan = build_cluster_fig(
            selected_dow, "DBSCAN", db_threshold, db_metric, db_speed,
            eps=eps, min_s_db=db_mins,
        )
        st.plotly_chart(fig_dbscan, width='stretch')

# ═══════════════════════════════════════════════════════════════
# Onglet HDBSCAN
# ═══════════════════════════════════════════════════════════════
with tab_hdbscan:
    col_ctrl, col_map = st.columns([1, 3], gap="medium")

    with col_ctrl:
        st.subheader("Paramètres HDBSCAN")
        hdb_metric = st.selectbox(
            "Métrique de distance", ["manhattan", "euclidean"],
            key="hdb_metric",
            help="manhattan = adapté à la grille orthogonale des rues de NYC",
        )
        hdb_threshold = st.slider(
            "Min points / heure", 200, 2000, 500, step=100,
            key="hdb_threshold",
            help="Seuil minimum garanti pour l'heure la plus creuse. Le budget total (N_carte) est calculé automatiquement : N_carte = seuil / p_min.",
        )
        hdb_speed = st.select_slider(
            "Tempo animation (s/heure)",
            options=[5000, 6000, 8000, 10000],
            value=5000,
            key="hdb_speed",
            format_func=lambda v: f"{v//1000} s/h",
        )
        hdb_mincs = st.slider("min_cluster_size", 10, 200, 50, step=5, key="hdb_mincs")
        hdb_mins  = st.slider("min_samples", 1, 30, 5, key="hdb_mins")
        hdb_method = st.radio(
            "cluster_selection_method", ["leaf", "eom"],
            key="hdb_method",
            help="**leaf** = granulaire (recommandé)  |  **eom** = stable (tend à tout fusionner)",
        )

    with col_map:
        fig_hdbscan = build_cluster_fig(
            selected_dow, "HDBSCAN", hdb_threshold, hdb_metric, hdb_speed,
            min_cs=hdb_mincs, min_s_hdb=hdb_mins, method=hdb_method,
        )
        st.plotly_chart(fig_hdbscan, width='stretch')
