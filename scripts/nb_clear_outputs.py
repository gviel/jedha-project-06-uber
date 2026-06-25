#!/usr/bin/env python3
"""nb_clear_outputs.py — effacer les outputs d'un notebook (réduit la taille du fichier).

Usage:
    python nb_clear_outputs.py notebook.ipynb             # tout effacer
    python nb_clear_outputs.py notebook.ipynb 12 15 20    # cellules spécifiques
    python nb_clear_outputs.py notebook.ipynb --dry-run
"""
import json, argparse, sys
from pathlib import Path


def clear_outputs(path, cell_specs=None, dry_run=False):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
        nb = json.loads(raw)

    cells = nb["cells"]
    n = len(cells)
    size_before = len(raw)

    if cell_specs:
        targets = []
        for spec in cell_specs:
            if ":" in spec:
                parts = spec.split(":")
                s = int(parts[0]) if parts[0] else 0
                e = int(parts[1]) if parts[1] else n - 1
                targets.extend(range(s, e + 1))
            else:
                targets.append(int(spec))
        targets = sorted(set(targets))
    else:
        targets = [i for i, c in enumerate(cells) if c["cell_type"] == "code"]

    cleared = 0
    for i in targets:
        if i < 0 or i >= n:
            continue
        cell = cells[i]
        if cell["cell_type"] != "code":
            continue
        if cell.get("outputs") or cell.get("execution_count") is not None:
            cell["outputs"] = []
            cell["execution_count"] = None
            cleared += 1

    print(f"Cellules nettoyées : {cleared}")

    if dry_run:
        print("[dry-run] aucune modification")
        return

    new_raw = json.dumps(nb, ensure_ascii=False, indent=1)
    size_after = len(new_raw)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_raw)
    gain = (size_before - size_after) / 1024
    print(f"✓ Taille : {size_before/1024:.0f} KB → {size_after/1024:.0f} KB  (−{gain:.0f} KB)")


def main():
    p = argparse.ArgumentParser(description="Effacer les outputs d'un notebook")
    p.add_argument("notebook", help="chemin vers le .ipynb")
    p.add_argument("cells", nargs="*", help="indices ou plages (vide = tout le notebook)")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    clear_outputs(args.notebook, args.cells if args.cells else None, args.dry_run)


if __name__ == "__main__":
    main()
