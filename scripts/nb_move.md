# nb_move.py — Déplacer un bloc de cellules

**Objectif :** réordonner des sections entières du notebook en déplaçant un bloc contigu de cellules.

```
python scripts/nb_move.py notebook.ipynb range after [--dry-run] [--backup]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `notebook` | Chemin vers le `.ipynb` |
| `range` | Plage de cellules à déplacer : `17:20` (4 cellules) ou cellule seule `17` |
| `after` | Insérer le bloc après la cellule N (dans la numérotation originale) |
| `--dry-run` | Simulation sans écriture |
| `--backup` | Crée `.ipynb.bak` avant modification |

**Contrainte :** `after` ne doit pas être à l'intérieur du bloc déplacé.

## Sortie

```
Déplacement cell-17:20 (4 cellules) → après cell-28
  cell-17: '### 4.5) Cleaning'
  cell-18: '# suppression des lignes avec pid=null'
  cell-19: 'On supprime les colonnes avec plus de 40%'
  cell-20: 'print(drop_candidates.index.tolist())'
✓ Déplacement effectué
```

## Comportement

L'index `after` est exprimé dans la **numérotation originale** (avant déplacement). Le script recalcule automatiquement la position d'insertion après avoir retiré le bloc de sa place initiale.

## Exemples

```bash
# Vérifier avant de modifier
python scripts/nb_move.py Tinder_GV.ipynb 17:20 28 --dry-run

# Déplacer une section avec backup
python scripts/nb_move.py Tinder_GV.ipynb 17:20 28 --backup

# Déplacer une cellule seule
python scripts/nb_move.py Tinder_GV.ipynb 28 35
```
