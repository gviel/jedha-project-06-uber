# Scripts de manipulation de notebooks Jupyter

Scripts CLI Python pour inspecter et modifier des fichiers `.ipynb` sans passer par Jupyter — utiles pour réduire la consommation de tokens lors d'interactions avec un LLM.

```bash
python scripts/<script>.py notebook.ipynb [options]
```

## Scripts disponibles

| Script | Specs | Rôle |
|--------|-------|------|
| `nb_inspect.py` | [nb_inspect.md](nb_inspect.md) | Lister les cellules (index, type, aperçu, titres) |
| `nb_grep.py`    | [nb_grep.md](nb_grep.md)       | Rechercher un pattern regex dans les cellules |
| `nb_cat.py`     | [nb_cat.md](nb_cat.md)         | Afficher le contenu complet d'une ou plusieurs cellules |
| `nb_sed.py`     | [nb_sed.md](nb_sed.md)         | Remplacer du texte dans une cellule ou dans tout le notebook |
| `nb_insert.py`  | [nb_insert.md](nb_insert.md)   | Insérer une nouvelle cellule à une position précise |
| `nb_move.py`    | [nb_move.md](nb_move.md)       | Déplacer un bloc de cellules |
| `nb_delete.py`  | [nb_delete.md](nb_delete.md)   | Supprimer des cellules |
| `nb_replace.py` | [nb_replace.md](nb_replace.md) | Remplacer entièrement le contenu d'une cellule |
| `nb_clear_outputs.py` | [nb_clear_outputs.md](nb_clear_outputs.md) | Effacer les outputs (réduit la taille du fichier) |

---

## Conventions communes

**Indexation** : les cellules sont indexées à partir de **0**, indépendamment du compteur `In [N]:` de Jupyter.

**Plages** : partout où un index est accepté, une plage `start:end` (bornes inclusives) est valide :
```
17      → cellule 17
17:20   → cellules 17, 18, 19, 20
:5      → cellules 0 à 5
20:     → cellule 20 jusqu'à la fin
```

**Options communes aux scripts d'écriture** :

| Option | Effet |
|--------|-------|
| `--dry-run` | Simule l'opération sans écrire |
| `--backup`  | Crée un `.ipynb.bak` avant modification |

**Outputs réinitialisés** : tout script qui modifie une cellule code remet ses `outputs` à `[]` et `execution_count` à `None`.

---

## Workflow typique avec un LLM

```bash
# 1. Identifier la structure sans charger le contenu
python scripts/nb_inspect.py notebook.ipynb --headers

# 2. Localiser les cellules à modifier
python scripts/nb_grep.py notebook.ipynb "my_var"

# 3. Lire uniquement la cellule ciblée
python scripts/nb_cat.py notebook.ipynb 27

# 4. Appliquer la modification
python scripts/nb_sed.py notebook.ipynb 27 "old_text" "new_text"

# 5. Nettoyer les outputs avant de passer le notebook au LLM
python scripts/nb_clear_outputs.py notebook.ipynb
```
