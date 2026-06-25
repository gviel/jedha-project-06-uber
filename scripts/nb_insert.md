# nb_insert.py — Insérer une cellule

**Objectif :** ajouter une nouvelle cellule à une position précise, depuis un fichier ou en ligne.

```
python scripts/nb_insert.py notebook.ipynb after --type {code|markdown} (--file FILE | --text TEXT) [--dry-run]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `notebook` | Chemin vers le `.ipynb` |
| `after` | Insérer après la cellule N — `-1` pour tout début du notebook |
| `--type` | `code` (défaut) ou `markdown` |
| `--file` | Fichier `.py` ou `.md` dont le contenu devient la cellule |
| `--text` | Contenu inline entre guillemets |
| `--dry-run` | Simulation sans écriture |

`--file` et `--text` sont mutuellement exclusifs.

## Sortie

```
Insertion [code] à la position 28 (après cell-27)
Aperçu : 'df_cleaned\n'
✓ Notebook : 42 → 43 cellules  (nouvelle cell-28)
```

## Exemples

```bash
# Insérer une cellule depuis un fichier préparé
python scripts/nb_insert.py Tinder_GV.ipynb 27 --file scripts/new_analysis.py

# Insérer un titre markdown
python scripts/nb_insert.py Tinder_GV.ipynb 16 --type markdown --text "### 4.4) Vérification"

# Insérer une cellule de debug rapide
python scripts/nb_insert.py Tinder_GV.ipynb 20 --text "print(df_cleaned.shape)"

# Insérer en tête de notebook
python scripts/nb_insert.py Tinder_GV.ipynb -1 --type code --file scripts/setup.py
```
