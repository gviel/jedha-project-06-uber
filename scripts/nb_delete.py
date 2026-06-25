#!/usr/bin/env python3
"""nb_delete.py — supprimer une ou plusieurs cellules d'un notebook.

Usage:
    python nb_delete.py notebook.ipynb 18
    python nb_delete.py notebook.ipynb 18 20 25
    python nb_delete.py notebook.ipynb 18:22          # plage inclusive
    python nb_delete.py notebook.ipynb 18 --dry-run
"""
import json, argparse, shutil, sys
from pathlib import Path


def parse_specs(specs, n_cells):
    indices = []
    for spec in specs:
        if ":" in spec:
            parts = spec.split(":")
            start = int(parts[0]) if parts[0] else 0
            end   = int(parts[1]) if parts[1] else n_cells - 1
            indices.extend(range(start, end + 1))
        else:
            indices.append(int(spec))
    return sorted(set(indices))


def delete(path, cell_specs, dry_run=False, backup=False):
    with open(path, encoding="utf-8") as f:
        nb = json.load(f)
    cells = nb["cells"]
    n = len(cells)

    to_delete = parse_specs(cell_specs, n)
    invalid = [i for i in to_delete if i < 0 or i >= n]
    if invalid:
        print(f"Indices hors limites : {invalid}  (max {n-1})", file=sys.stderr)
        sys.exit(1)

    print(f"Suppression de {len(to_delete)} cellule(s) :")
    for i in to_delete:
        src = "".join(cells[i].get("source", []))
        preview = src[:70].replace("\n", " | ")
        print(f"  cell-{i:02d}  [{cells[i]['cell_type'][:4]}]  {preview!r}")

    if dry_run:
        print("[dry-run] aucune modification")
        return

    if backup:
        bak = Path(path).with_suffix(".ipynb.bak")
        shutil.copy2(path, bak)
        print(f"Backup : {bak}")

    nb["cells"] = [c for i, c in enumerate(cells) if i not in set(to_delete)]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print(f"✓ Notebook : {n} → {n - len(to_delete)} cellules")


def main():
    p = argparse.ArgumentParser(description="Supprimer des cellules d'un notebook")
    p.add_argument("notebook", help="chemin vers le .ipynb")
    p.add_argument("cells", nargs="+", help="indices ou plages  ex: 18   18:22   3 7")
    p.add_argument("--dry-run", action="store_true", help="simulation sans écriture")
    p.add_argument("--backup", action="store_true", help="créer un .bak avant suppression")
    args = p.parse_args()
    delete(args.notebook, args.cells, args.dry_run, args.backup)


if __name__ == "__main__":
    main()
