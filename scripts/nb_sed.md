# nb_sed.py — Remplacer du texte

**Objectif :** substitution ciblée d'un texte dans une cellule ou dans tout le notebook, sans réécrire la cellule entière.

```
python scripts/nb_sed.py notebook.ipynb cell old new [--dry-run] [--backup]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `notebook` | Chemin vers le `.ipynb` |
| `cell` | Index de cellule ou `all` pour tout le notebook |
| `old` | Texte exact à remplacer (toutes les occurrences dans la cellule) |
| `new` | Texte de remplacement |
| `--dry-run` | Simulation sans écriture |
| `--backup` | Crée `.ipynb.bak` avant modification |

## Sortie

```
cell-20: 3 remplacement(s)
✓ 1 cellule(s) modifiée(s) — outputs réinitialisés
```

**Code de sortie :** `1` si le texte `old` est introuvable dans les cellules ciblées.

## Comportement

- Remplace **toutes** les occurrences de `old` dans la cellule ciblée.
- Réinitialise `outputs` et `execution_count` de chaque cellule modifiée.
- Avec `all`, parcourt toutes les cellules et modifie celles qui contiennent `old`.

## Exemples

```bash
# Corriger une référence de variable dans une cellule précise
python scripts/nb_sed.py Tinder_GV.ipynb 27 "df_cleaned" "df_cleaned_1"

# Renommer une variable dans tout le notebook (vérifier d'abord)
python scripts/nb_sed.py Tinder_GV.ipynb all "df_cleaned" "df_work" --dry-run
python scripts/nb_sed.py Tinder_GV.ipynb all "df_cleaned" "df_work" --backup

# Corriger un appel de méthode
python scripts/nb_sed.py Tinder_GV.ipynb 27 ".drop(drop_final)" ".drop(columns=drop_final)"
```
