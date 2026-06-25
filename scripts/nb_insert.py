#!/usr/bin/env python3
"""nb_insert.py — insérer une cellule dans un notebook.

Usage:
    python nb_insert.py notebook.ipynb 15 --type code --file new_cell.py
    python nb_insert.py notebook.ipynb 15 --type markdown --text "### 4.6) Analyse"
    python nb_insert.py notebook.ipynb -1 --type code --file header.py   # début
    python nb_insert.py notebook.ipynb 15 --type code --file cell.py --dry-run
"""
import json, argparse, sys
from pathlib import Path


def text_to_source(text: str) -> list:
    """Convertit un texte en liste de lignes au format Jupyter source."""
    lines = text.split("\n")
    src = [l + "\n" for l in lines[:-1]]
    if lines[-1]:
        src.append(lines[-1])
    return src


def make_cell(cell_type, source):
    cell = {"cell_type": cell_type, "metadata": {}, "source": source}
    if cell_type == "code":
        cell["outputs"] = []
        cell["execution_count"] = None
    return cell


def insert(path, after, cell_type, content, dry_run=False):
    with open(path, encoding="utf-8") as f:
        nb = json.load(f)
    cells = nb["cells"]
    n = len(cells)

    if after < -1 or after >= n:
        print(f"Position {after} hors limites (-1 à {n-1})", file=sys.stderr)
        sys.exit(1)

    new_cell = make_cell(cell_type, content)
    insert_pos = after + 1

    preview = "".join(content)[:120].replace("\n", " | ")
    print(f"Insertion [{cell_type}] à la position {insert_pos} (après cell-{after})")
    print(f"Aperçu : {preview!r}")

    if dry_run:
        print("[dry-run] aucune modification")
        return

    cells.insert(insert_pos, new_cell)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print(f"✓ Notebook : {n} → {n+1} cellules  (nouvelle cell-{insert_pos})")


def main():
    p = argparse.ArgumentParser(description="Insérer une cellule dans un notebook")
    p.add_argument("notebook", help="chemin vers le .ipynb")
    p.add_argument("after", type=int, help="insérer après la cellule N  (-1 = tout début)")
    p.add_argument("--type", choices=["code", "markdown"], default="code",
                   dest="cell_type", help="type de cellule (défaut: code)")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--file", help="fichier source à insérer (.py ou .md)")
    src.add_argument("--text", help="contenu inline (guillemets)")
    p.add_argument("--dry-run", action="store_true", help="simulation sans écriture")
    args = p.parse_args()

    if args.file:
        content = Path(args.file).read_text(encoding="utf-8")
    else:
        content = args.text

    insert(args.notebook, args.after, args.cell_type, text_to_source(content), args.dry_run)


if __name__ == "__main__":
    main()
