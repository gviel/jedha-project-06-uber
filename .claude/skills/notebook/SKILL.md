---
description: Opérations sur un notebook Jupyter — utilise les scripts dédiés
paths:
  - "*.ipynb"
  - "scripts/*.py"
allowed-tools: Bash, Write
---

## Notebook actif

Le notebook par défaut de ce projet est `Uber_GV.ipynb`.
Si l'utilisateur mentionne explicitement un autre fichier `.ipynb`, utiliser celui-là à la place dans tous les appels de scripts. Dans le doute, utiliser `Uber_GV.ipynb`.

## Structure actuelle (notebook par défaut)
!`python scripts/nb_inspect.py Uber_GV.ipynb --headers`

## Cellules code
!`python scripts/nb_inspect.py Uber_GV.ipynb --code`

---

## Règle 1 — Réutiliser les scripts existants en priorité

Avant toute opération :
1. Vérifier si un script dans `scripts/` couvre déjà le besoin (`scripts/README.md`)
2. Utiliser le script existant — ne jamais charger le fichier `.ipynb` entier via `Read` ou `cat`

Remplacer `<nb>` par le notebook actif dans tous les appels :

| Besoin | Script |
|--------|--------|
| Structure / headers | `python scripts/nb_inspect.py <nb> --headers` |
| Liste des cellules  | `python scripts/nb_inspect.py <nb> [--code\|--md]` |
| Lire une cellule    | `python scripts/nb_cat.py <nb> <idx\|range>` |
| Chercher du texte   | `python scripts/nb_grep.py <nb> "<pattern>" [--code\|--md]` |
| Remplacer du texte  | `python scripts/nb_sed.py <nb> <idx> "<old>" "<new>"` |
| Réécrire une cellule | `python scripts/nb_replace.py <nb> <idx> --file /tmp/cell.py` |
| Déplacer des cells  | `python scripts/nb_move.py <nb> <range> <after>` |
| Supprimer des cells | `python scripts/nb_delete.py <nb> <idx>` |
| Effacer outputs     | `python scripts/nb_clear_outputs.py <nb>` |

---

## Règle 2 — Workflow de modification

1. **Chercher** d'abord : `python scripts/nb_grep.py <nb> "<pattern>"`
2. **Lire** la cellule cible : `python scripts/nb_cat.py <nb> <idx>`
3. **Modifier** :
   - Changement ciblé → `nb_sed.py <nb> <idx> "<old>" "<new>" --backup`
   - Réécriture → écrire dans `/tmp/cell_<idx>.py`, puis `nb_replace.py <nb> <idx> --file /tmp/cell_<idx>.py --backup`
4. **Confirmer** : `python scripts/nb_cat.py <nb> <idx>`

Utiliser `--backup` sur toute modification qui supprime ou réécrit du contenu.
