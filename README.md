# JEDHA CDSD Certification (Bloc 3) — Projet #6 Uber

Identification des **hot-zones** où les chauffeurs Uber devraient se positionner selon le moment de la journée (NYC, 2014).

Dataset : ~4,5 M de courses Uber (avril–septembre 2014) — [Kaggle](https://www.kaggle.com/datasets/fivethirtyeight/uber-pickups-in-new-york-city).

---

## Structure du projet

```
Uber_GV.ipynb              Notebook d'analyse principal
01-Uber_Pickups.ipynb      Énoncé (référence, ne pas modifier)
dashboard/
  app.py                   Dashboard Streamlit interactif
  prepare_data.py          Script de préparation du dataset
data/
  uber-trip-data/2014/     CSV bruts (non versionnés)
  dashboard_sept2w.parquet Dataset préparé pour le dashboard
exports/                   Figures générées (non versionnées)
env_uber.yml               Environnement conda
```

---

## Installation

```bash
conda env create -f env_uber.yml
conda activate uber
```

---

## Notebook d'analyse (`Uber_GV.ipynb`)

```bash
jupyter notebook Uber_GV.ipynb
```

### Sections

| Section | Contenu |
|---------|---------|
| §1.1 | Nombre de courses par mois (2014–2015) |
| §1.2 | Positions géographiques des bases TLC |
| §1.3 | Chargement des ~4,5 M de courses 2014 |
| §1.4 | Analyse du trafic par jour de semaine et par heure |
| §2.1 | Réduction au sous-ensemble jeudi/septembre/16h–19h |
| §2.2 | KMeans — identification de 20 hot-zones |
| §2.3 | DBSCAN — clustering par densité (métrique Manhattan) |
| §2.4 | HDBSCAN — clustering hiérarchique adaptatif |
| §2.5 | H3 — binning hexagonal par densité de pickups |

---

## Dashboard interactif (`dashboard/app.py`)

### Préparation des données (une seule fois)

```bash
conda activate uber
cd /chemin/vers/Project_06_Uber
python dashboard/prepare_data.py
```

Génère `data/dashboard_sept2w.parquet` (~480 k courses, 2 premières semaines de septembre 2014, 1,6 Mo).

### Lancement

```bash
conda activate uber
streamlit run dashboard/app.py
# → http://localhost:8501
```

### Fonctionnalités

**Filtres (sidebar)**

- Sélection du jour de la semaine (boutons pills Lun–Dim)
- Plage horaire 0h–23h (slider) ou mode nuit avec traversée de minuit (ex. 19h→06h)
- Taille d'échantillon N — sampling stratifié par heure : chaque heure reçoit une part de N proportionnelle à son poids dans la sélection

**Onglet H3 — Binning hexagonal**

- Slider de résolution 6–10 (résolution 8 ≈ 0,1 km²/hex, adapté aux blocs de rues NYC)
- Carte choroplèthe colorée par densité de pickups (YlOrRd)

**Onglet DBSCAN / HDBSCAN**

- Toggle DBSCAN ↔ HDBSCAN
- Paramètres ajustables : métrique (manhattan recommandé pour la grille NYC), eps, min\_samples, min\_cluster\_size, cluster\_selection\_method
- Carte des clusters colorés par importance + centroides proportionnels
- Métriques : nombre de hot-zones, points classifiés, points bruit

---

## Algorithmes comparés

| Algorithme | Paramètre clé | Avantage |
|------------|---------------|----------|
| KMeans | `n_clusters` | Simple, interprétable, nombre de zones fixé |
| DBSCAN | `eps` (m), `min_samples` | Détecte les formes arbitraires, rejette le bruit |
| HDBSCAN | `min_cluster_size`, `method=leaf` | Gère les densités variables, pas d'`eps` à calibrer |
| H3 | `resolution` | Couverture exhaustive, reproductible, sans hyperparamètre de distance |

Métrique de distance : **Manhattan** (`|Δx| + |Δy|`) — cohérente avec la grille orthogonale des rues de NYC.
