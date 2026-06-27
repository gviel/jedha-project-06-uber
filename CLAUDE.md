# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

JEDHA certification project (bloc #3) — Unsupervised learning on Uber pickup data (NYC, 2014).
Goal: identify hot-zones where drivers should be at any given time of day.
Deliverable: Jupyter notebook with clustering analysis (KMeans + DBSCAN) and interactive Plotly maps.

Dataset: ~4.5M Uber pickups (April–September 2014), NYC.

## Environment Setup

```bash
conda env create -f env_uber.yml
conda activate uber
```

Key packages: `pandas`, `numpy`, `plotly`, `scikit-learn`, `geopandas`, `shapely`.

## Running the Notebook

```bash
jupyter notebook Uber_GV.ipynb
```

The notebook kernel must be set to the `uber` conda environment (`ipykernel` is included).

## Versioning — règles de commit & push

### Deux branches, deux usages
- `dev` : branche de travail
- `main` : branche livrable (déploiement Streamlit Cloud)

### Workflow standard (sur dev)
```bash
git add <fichiers>
git commit -m "..."
```

### Publication vers main
```bash
git checkout main
git merge dev
git checkout dev
git push origin dev && git push origin main
```

## Architecture

- `01-Uber_Pickups.ipynb` — project brief (read-only reference)
- `Uber_GV.ipynb` — main analysis notebook
- `data/` — données brutes (non versionnées — trop volumineuses)
- `resources/` — références NYC taxi zones (non versionnées)
- `exports/` — figures générées (non versionnées)
- `scripts/` — outils CLI pour manipuler le notebook
- `.claude/` — configuration Claude Code (non versionné sur main)
