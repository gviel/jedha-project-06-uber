# nb_grep.py — Chercher du texte

**Objectif :** localiser toutes les occurrences d'un pattern regex dans les cellules.

```
python scripts/nb_grep.py notebook.ipynb pattern [-i] [--code] [--md]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `notebook` | Chemin vers le `.ipynb` |
| `pattern` | Expression régulière Python |
| `-i`, `--ignore-case` | Recherche insensible à la casse |
| `--code` | Restreindre aux cellules code |
| `--md` | Restreindre aux cellules markdown |

## Sortie

```
cell-20:  8  [code]      mask_w69    = df['wave'].between(6, 9)
cell-30:  2  [code]  df_cleaned_F = df_cleaned[df['gender']==0]
```

Format : `cell-{idx}:{ligne}  [{type}]  {contenu de la ligne}`

**Code de sortie :** `1` si aucune occurrence trouvée.

## Exemples

```bash
# Trouver toutes les références à une variable
python scripts/nb_grep.py Tinder_GV.ipynb "df_cleaned"

# Trouver les sections numérotées dans les titres markdown
python scripts/nb_grep.py Tinder_GV.ipynb "^#{1,3} [0-9]" --md

# Chercher un appel de fonction dans le code
python scripts/nb_grep.py Tinder_GV.ipynb "dropna\(" --code

# Recherche insensible à la casse
python scripts/nb_grep.py Tinder_GV.ipynb "cleaning" -i --md
```
