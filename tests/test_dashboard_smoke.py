"""Smoke test du dashboard Streamlit — régression structure et paramètres.

Vérifie sans lancer de browser :
- imports OK (dépendances présentes)
- 4 onglets déclarés (H3, KMeans, DBSCAN, HDBSCAN)
- paramètres de chaque onglet présents dans le source
- build_cluster_fig supporte KMeans

Lancement :
    conda run -n uber python tests/test_dashboard_smoke.py
"""
import ast
import sys
from pathlib import Path

SRC = Path(__file__).parent.parent / "dashboard" / "app.py"


def check(condition: bool, label: str):
    status = "OK" if condition else "FAIL"
    print(f"  [{status}] {label}")
    if not condition:
        sys.exit(1)


src = SRC.read_text()

print("=== Smoke test dashboard/app.py ===")

print("\n[Syntaxe]")
try:
    ast.parse(src)
    check(True, "syntaxe Python valide")
except SyntaxError as e:
    check(False, f"erreur de syntaxe : {e}")

print("\n[Imports]")
check("from sklearn.cluster import DBSCAN, HDBSCAN, KMeans" in src, "import KMeans")
check("import h3" in src,                                            "import h3")
check("import streamlit as st" in src,                               "import streamlit")

print("\n[Onglets — 4 tabs]")
check('tab_h3, tab_kmeans, tab_dbscan, tab_hdbscan = st.tabs' in src, "déclaration 4 onglets")
check('"H3 — Binning hexagonal"' in src, 'onglet H3')
check('"KMeans"'                 in src, 'onglet KMeans')
check('"DBSCAN"'                 in src, 'onglet DBSCAN')
check('"HDBSCAN"'                in src, 'onglet HDBSCAN')

print("\n[Paramètres KMeans]")
check('key="km_k"'         in src, 'slider Nombre de clusters (km_k)')
check('key="km_threshold"' in src, 'slider Min points / heure (km_threshold)')
check('key="km_speed"'     in src, 'select_slider Tempo animation (km_speed)')
check('n_clusters=km_k'    in src, 'appel build_cluster_fig avec n_clusters')

print("\n[Paramètres DBSCAN]")
check('key="db_metric"'    in src, 'selectbox métrique (db_metric)')
check('key="db_eps"'       in src, 'slider eps (db_eps)')
check('key="db_mins"'      in src, 'slider min_samples (db_mins)')

print("\n[Paramètres HDBSCAN]")
check('key="hdb_metric"'   in src, 'selectbox métrique (hdb_metric)')
check('key="hdb_mincs"'    in src, 'slider min_cluster_size (hdb_mincs)')
check('key="hdb_method"'   in src, 'radio cluster_selection_method (hdb_method)')

print("\n[build_cluster_fig]")
check('n_clusters: int = 20'       in src, 'paramètre n_clusters dans la signature')
check('else:  # KMeans'            in src, 'branche KMeans dans le if/else')
check('KMeans(n_clusters=n_clusters' in src, 'instanciation KMeans')

print("\n=== Tous les checks passent ===")
