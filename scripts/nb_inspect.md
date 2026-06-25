# nb_inspect.py — Lister les cellules

**Objectif :** vue d'ensemble rapide du notebook sans charger son contenu.

```
python scripts/nb_inspect.py notebook.ipynb [--code] [--md] [--headers]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `notebook` | Chemin vers le `.ipynb` |
| `--code` | N'afficher que les cellules code |
| `--md` | N'afficher que les cellules markdown |
| `--headers` | N'afficher que les lignes de titre markdown (`#`, `##`, `###`, …) |

## Sortie

**Mode normal :**
```
idx  TYPE   exec    nL   première ligne
  0  MD            3L   '# JEDHA | Projet TINDER'
  3  CODE  [5]     4L   'import pandas as pd'
 12  CODE         22L   '# Calcul des valeurs nulles'

42 cellules total  (18 code, 24 markdown)
```

**Mode `--headers` :**
```
cell-00  # JEDHA | Projet TINDER
cell-04  ### 4.1) Chargement des données
cell-17  ### 4.4) Vérification
cell-24  ### 4.5) Cleaning
```

## Exemples

```bash
# Repérer la structure du notebook avant de modifier
python scripts/nb_inspect.py Tinder_GV.ipynb --headers

# Trouver l'index d'une cellule code spécifique
python scripts/nb_inspect.py Tinder_GV.ipynb --code

# Repérer les cellules vides (0L)
python scripts/nb_inspect.py Tinder_GV.ipynb | grep " 0L "
```
