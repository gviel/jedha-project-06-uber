# nb_delete.py — Supprimer des cellules

**Objectif :** supprimer des cellules vides, de debug ou obsolètes.

```
python scripts/nb_delete.py notebook.ipynb cell [cell ...] [--dry-run] [--backup]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `notebook` | Chemin vers le `.ipynb` |
| `cell` | Un ou plusieurs indices ou plages (`18`, `18:22`, `3 7 12`) |
| `--dry-run` | Simulation sans écriture |
| `--backup` | Crée `.ipynb.bak` avant suppression |

## Sortie

```
Suppression de 2 cellule(s) :
  cell-18  [mark]  ''
  cell-36  [code]  ''
✓ Notebook : 42 → 40 cellules
```

## Exemples

```bash
# Repérer les cellules vides puis les supprimer
python scripts/nb_inspect.py Tinder_GV.ipynb | grep " 0L "
python scripts/nb_delete.py Tinder_GV.ipynb 18 36 --dry-run
python scripts/nb_delete.py Tinder_GV.ipynb 18 36

# Supprimer une plage de cellules de debug
python scripts/nb_delete.py Tinder_GV.ipynb 30:32 --backup

# Supprimer des cellules non contiguës
python scripts/nb_delete.py Tinder_GV.ipynb 5 12 18 25
```
