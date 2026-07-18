# JEDHA CDSD Certification (Bloc 3) — Projet #6 Uber

**Dépôt GitHub** : https://github.com/gviel/jedha-project-06-uber

**Dashboard** : https://jedha-project-06-uber-e5a6exs9vw6pv6o6onweus.streamlit.app/

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
  dashboard_sept2w.parquet Dataset préparé (non versionné)
data/
  uber-trip-data/2014/     CSV bruts (non versionnés)
  stats_by_month.csv       Statistiques par mois (générées par tools/stats.sh)
exports/                   Figures générées (non versionnées)
tools/                     Scripts d'extraction géo et statistiques
env_uber.yml               Environnement conda
requirements.txt           Dépendances Python (Streamlit Cloud)
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
python dashboard/prepare_data.py
```

Génère `dashboard/dashboard_sept2w.parquet` (~480 k courses, 2 premières semaines de septembre 2014) et l'uploade sur S3.

### Lancement local

```bash
conda activate uber
streamlit run dashboard/app.py
# → http://localhost:8501
```

### Fonctionnalités

**Sidebar**

- Sélection du jour de la semaine (boutons pills Lun–Dim)

**Onglet H3 — Binning hexagonal**

- Résolution hexagonale 6–10 (résolution 8 ≈ 0,1 km²/hex, adapté aux blocs de rues NYC)
- Tempo d'animation par heure
- Budget total de points N — sampling stratifié, chaque heure reçoit une fraction proportionnelle à son poids
- Carte choroplèthe animée (heure par heure) colorée par densité de pickups

**Onglet DBSCAN**

- Métrique de distance (manhattan recommandé pour la grille NYC)
- Seuil minimum de points par heure (budget adaptatif)
- Paramètres : `eps` (m), `min_samples`
- Carte animée des clusters + centroides proportionnels au volume

**Onglet HDBSCAN**

- Métrique de distance
- Seuil minimum de points par heure
- Paramètres : `min_cluster_size`, `min_samples`, `cluster_selection_method` (leaf / eom)
- Carte animée des clusters + centroides proportionnels au volume

---

## Algorithmes comparés

| Algorithme | Paramètre clé | Avantage |
|------------|---------------|----------|
| KMeans | `n_clusters` | Simple, interprétable, nombre de zones fixé |
| DBSCAN | `eps` (m), `min_samples` | Détecte les formes arbitraires, rejette le bruit |
| HDBSCAN | `min_cluster_size`, `method=leaf` | Gère les densités variables, pas d'`eps` à calibrer |
| H3 | `resolution` | Couverture exhaustive, reproductible, sans hyperparamètre de distance |

Métrique de distance : **Manhattan** (`|Δx| + |Δy|`) — cohérente avec la grille orthogonale des rues de NYC.

---

## Dashboard en production

👉 **https://jedha-project-06-uber-e5a6exs9vw6pv6o6onweus.streamlit.app/**

---

## Déploiement Streamlit Community Cloud

L'app est déployable directement depuis la branche `main` :

- **Repository** : `gviel/jedha-project-06-uber`
- **Branch** : `main`
- **Main file** : `dashboard/app.py`

Les données sont lues depuis S3 (`s3://cdsd-uber-data/dashboard_sept2w.parquet`).
Ajouter les credentials AWS dans les secrets de l'app (Settings → Secrets) :

```toml
[aws]
access_key_id = "AKIA..."
secret_access_key = "..."
region = "eu-west-3"
```
