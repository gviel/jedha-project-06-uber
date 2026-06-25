#!/usr/bin/env python3
"""nb_replace.py — remplacer entièrement le contenu d'une cellule.

Usage:
    python nb_replace.py notebook.ipynb 27 --file new_code.py
    python nb_replace.py notebook.ipynb 27 --file cell.md --type markdown
    python nb_replace.py notebook.ipynb 27 --text "print('hello')"
    python nb_replace.py notebook.ipynb 27 --file new.py --dry-run
"""
import json, argparse, shutil, sys
from pathlib import Path


def text_to_source(text: str) -> list:
    """Convertit un texte en liste de lignes au format Jupyter source."""
    lines = text.split("\n")
    src = [l + "\n" for l in lines[:-1]]
    if lines[-1]:
        src.append(lines[-1])
    return src


def replace(path, cell_idx, content, cell_type=None, dry_run=False, backup=False):
    with open(path, encoding="utf-8") as f:
        nb = json.load(f)
    cells = nb["cells"]
    n = len(cells)

    if cell_idx < 0 or cell_idx >= n:
        print(f"cell-{cell_idx} hors limites (0–{n-1})", file=sys.stderr)
        sys.exit(1)

    cell = cells[cell_idx]
    old_src = "".join(cell.get("source", []))
    old_type = cell["cell_type"]

    effective_type = cell_type or old_type
    if effective_type != old_type:
        print(f"Type : {old_type} → {effective_type}")

    print(f"cell-{cell_idx}  [{old_type}]  ancien contenu ({len(old_src)} chars):")
    print(f"  {old_src[:80].replace(chr(10), ' | ')!r}")
    print(f"Nouveau contenu ({len(content)} chars):")
    print(f"  {content[:80].replace(chr(10), ' | ')!r}")

    if dry_run:
        print("[dry-run] aucune modification")
        return

    if backup:
        bak = Path(path).with_suffix(".ipynb.bak")
        shutil.copy2(path, bak)
        print(f"Backup : {bak}")

    cell["source"] = text_to_source(content)
    cell["cell_type"] = effective_type
    if effective_type == "code":
        cell["outputs"] = []
        cell["execution_count"] = None
    else:
        cell.pop("outputs", None)
        cell.pop("execution_count", None)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print("✓ Cellule remplacée — outputs réinitialisés")


def main():
    p = argparse.ArgumentParser(description="Remplacer entièrement le contenu d'une cellule")
    p.add_argument("notebook", help="chemin vers le .ipynb")
    p.add_argument("cell", type=int, help="index de la cellule")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--file", help="fichier source (.py ou .md)")
    src.add_argument("--text", help="contenu inline")
    p.add_argument("--type", choices=["code", "markdown"],
                   help="forcer le type (défaut : type existant)")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--backup", action="store_true")
    args = p.parse_args()

    content = Path(args.file).read_text(encoding="utf-8") if args.file else args.text
    replace(args.notebook, args.cell, content, args.type, args.dry_run, args.backup)


if __name__ == "__main__":
    main()
