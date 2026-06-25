#!/usr/bin/env python3
"""nb_sed.py — remplacer du texte dans une cellule ou dans tout le notebook.

Usage:
    python nb_sed.py notebook.ipynb 27 "df_cleaned" "df_cleaned_1"
    python nb_sed.py notebook.ipynb all "df_cleaned" "df"
    python nb_sed.py notebook.ipynb 27 "old" "new" --dry-run
    python nb_sed.py notebook.ipynb 27 "old" "new" --backup
"""
import json, argparse, shutil, sys
from pathlib import Path


def sed(path, cell_spec, old, new, dry_run=False, backup=False):
    with open(path, encoding="utf-8") as f:
        nb = json.load(f)
    cells = nb["cells"]
    n = len(cells)

    targets = list(range(n)) if cell_spec == "all" else [int(cell_spec)]

    changed = 0
    for i in targets:
        if i < 0 or i >= n:
            print(f"cell-{i} hors limites (0–{n-1})", file=sys.stderr)
            continue
        src = "".join(cells[i].get("source", []))
        count = src.count(old)
        if count == 0:
            continue
        new_src = src.replace(old, new)
        print(f"cell-{i:02d}: {count} remplacement(s)")
        if not dry_run:
            cells[i]["source"] = new_src
            cells[i]["outputs"] = [] if cells[i]["cell_type"] == "code" else cells[i].get("outputs")
            cells[i]["execution_count"] = None if cells[i]["cell_type"] == "code" else cells[i].get("execution_count")
        changed += 1

    if changed == 0:
        print(f"Texte introuvable dans les cellules ciblées.", file=sys.stderr)
        sys.exit(1)

    if dry_run:
        print(f"[dry-run] {changed} cellule(s) seraient modifiées — aucune écriture")
        return

    if backup:
        bak = Path(path).with_suffix(".ipynb.bak")
        shutil.copy2(path, bak)
        print(f"Backup : {bak}")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print(f"✓ {changed} cellule(s) modifiée(s) — outputs réinitialisés")


def main():
    p = argparse.ArgumentParser(description="Remplacer du texte dans un notebook")
    p.add_argument("notebook", help="chemin vers le .ipynb")
    p.add_argument("cell", help="index de cellule ou 'all'")
    p.add_argument("old", help="texte à remplacer")
    p.add_argument("new", help="texte de remplacement")
    p.add_argument("--dry-run", action="store_true", help="simulation sans écriture")
    p.add_argument("--backup", action="store_true", help="créer un .bak avant modification")
    args = p.parse_args()
    sed(args.notebook, args.cell, args.old, args.new, args.dry_run, args.backup)


if __name__ == "__main__":
    main()
