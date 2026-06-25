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
- `dev` : branche de travail complète (Claude Code inclus — `.claude/`, `CLAUDE.md`, `scripts/`, `exports/`)
- `main` : branche livrable (uniquement les fichiers visibles du correcteur)

### Workflow standard (sur dev)
```bash
git add <fichiers>
git commit -m "..."
git push origin dev
```

### Publication vers main — règle absolue
Ne jamais faire `git merge dev` ni committer directement sur `main`.
Utiliser exclusivement le script de sync :
```bash
bash scripts/sync_main.sh                        # message demandé interactivement
bash scripts/sync_main.sh dev "§X.Y résumé"   # message en argument
git push origin dev && git push origin main
```

## Architecture

- `01-Uber_Pickups.ipynb` — project brief (read-only reference)
- `Uber_GV.ipynb` — main analysis notebook
- `data/` — données brutes (non versionnées — trop volumineuses)
- `resources/` — références NYC taxi zones (non versionnées)
- `exports/` — figures générées (non versionnées)
- `scripts/` — outils CLI pour manipuler le notebook (non versionnés sur main)
- `.claude/` — configuration Claude Code (non versionné sur main)
