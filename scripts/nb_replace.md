# nb_replace.py — Remplacer entièrement une cellule

**Objectif :** réécrire complètement le contenu d'une cellule depuis un fichier ou un texte inline. À utiliser quand les modifications sont trop importantes pour `nb_sed.py`.

```
python scripts/nb_replace.py notebook.ipynb cell (--file FILE | --text TEXT) [--type {code|markdown}] [--dry-run] [--backup]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `notebook` | Chemin vers le `.ipynb` |
| `cell` | Index de la cellule à remplacer |
| `--file` | Fichier source dont le contenu remplace intégralement la cellule |
| `--text` | Nouveau contenu inline |
| `--type` | Forcer le type (`code` ou `markdown`) ; par défaut conserve le type existant |
| `--dry-run` | Simulation sans écriture |
| `--backup` | Crée `.ipynb.bak` avant modification |

`--file` et `--text` sont mutuellement exclusifs.

## Sortie

```
cell-27  [code]  ancien contenu (245 chars):
  'import re\nfrom collections import defaultdict\n...'
Nouveau contenu (512 chars):
  'import re\nfrom collections ...'
✓ Cellule remplacée — outputs réinitialisés
```

## Workflow recommandé

1. Extraire la cellule actuelle : `python scripts/nb_cat.py notebook.ipynb 27 > cell_27.py`
2. Éditer `cell_27.py` avec un éditeur
3. Injecter : `python scripts/nb_replace.py notebook.ipynb 27 --file cell_27.py`

## Exemples

```bash
# Remplacer depuis un fichier préparé
python scripts/nb_replace.py Tinder_GV.ipynb 27 --file scripts/cell_27_new.py

# Remplacer avec backup
python scripts/nb_replace.py Tinder_GV.ipynb 27 --file scripts/cell_27_new.py --backup

# Convertir une cellule code en cellule markdown
python scripts/nb_replace.py Tinder_GV.ipynb 16 --file note.md --type markdown

# Vider une cellule (remplacer par un commentaire)
python scripts/nb_replace.py Tinder_GV.ipynb 36 --text "# TODO"
```
