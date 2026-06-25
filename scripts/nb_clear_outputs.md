# nb_clear_outputs.py — Effacer les outputs

**Objectif :** réduire la taille du fichier `.ipynb` en supprimant les outputs (graphiques Plotly, tableaux pandas, prints). Indispensable avant de passer le notebook à un LLM pour économiser des tokens.

```
python scripts/nb_clear_outputs.py notebook.ipynb [cell ...] [--dry-run]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `notebook` | Chemin vers le `.ipynb` |
| `cell` | Indices ou plages optionnels — si absent, nettoie **tout** le notebook |
| `--dry-run` | Affiche le gain estimé sans modifier le fichier |

## Sortie

```
Cellules nettoyées : 18
✓ Taille : 2840 KB → 187 KB  (−2653 KB)
```

## Comportement

- Remet `outputs` à `[]` et `execution_count` à `None` pour chaque cellule code ciblée.
- Les cellules markdown ne sont pas affectées.
- Sans argument de cellule : parcourt toutes les cellules code du notebook.

## Exemples

```bash
# Nettoyer tout le notebook avant de le donner à un LLM
python scripts/nb_clear_outputs.py Tinder_GV.ipynb

# Vérifier le gain avant de modifier
python scripts/nb_clear_outputs.py Tinder_GV.ipynb --dry-run

# Nettoyer seulement les cellules graphiques (les plus volumineuses)
python scripts/nb_clear_outputs.py Tinder_GV.ipynb 13 32 34

# Nettoyer une plage de cellules
python scripts/nb_clear_outputs.py Tinder_GV.ipynb 10:20
```
