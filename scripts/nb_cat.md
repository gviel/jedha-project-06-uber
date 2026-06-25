# nb_cat.py — Afficher le contenu d'une cellule

**Objectif :** lire le code exact d'une ou plusieurs cellules connues.

```
python scripts/nb_cat.py notebook.ipynb cell [cell ...] [-o]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `notebook` | Chemin vers le `.ipynb` |
| `cell` | Un ou plusieurs indices ou plages (`5`, `5:10`, `3 7 12`) |
| `-o`, `--outputs` | Afficher aussi les outputs (tronqués à 1000 chars) |

## Sortie

```
================================================================
# cell-27  [code]  exec=None
================================================================
import re
from collections import defaultdict

attr_bases_all = ['attr', 'sinc', 'intel', 'fun', 'amb', 'shar']
...

```

## Exemples

```bash
# Lire une cellule avant de la modifier
python scripts/nb_cat.py Tinder_GV.ipynb 27

# Lire plusieurs cellules disjointes
python scripts/nb_cat.py Tinder_GV.ipynb 17 20 24

# Lire une plage de cellules
python scripts/nb_cat.py Tinder_GV.ipynb 17:24

# Lire une cellule avec ses outputs
python scripts/nb_cat.py Tinder_GV.ipynb 12 -o
```
