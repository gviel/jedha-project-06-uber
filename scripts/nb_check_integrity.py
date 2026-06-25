#!/usr/bin/env python3
"""nb_check_integrity.py — détecter les cellules corrompues (source char-par-char).

Usage:
    python scripts/nb_check_integrity.py Uber_GV.ipynb
    python scripts/nb_check_integrity.py Uber_GV.ipynb --verbose
"""
import json, argparse, sys
from pathlib import Path


def check(path, verbose=False):
    with open(path, encoding="utf-8") as f:
        nb = json.load(f)

    corrupted = []
    for i, cell in enumerate(nb["cells"]):
        src = cell.get("source", [])
        if not src:
            continue
        # Source stockée comme string → itération char par char (avg=1.0)
        if isinstance(src, str):
            if len(src) > 10:
                corrupted.append((i, cell["cell_type"], "string", len(src), 1.0))
                continue
        # Source stockée comme liste
        if isinstance(src, list) and len(src) > 5:
            avg = sum(len(s) for s in src) / len(src)
            if avg <= 2.1:
                corrupted.append((i, cell["cell_type"], "list", len(src), avg))
            elif verbose:
                print(f"  cell-{i:02d} [{cell['cell_type']}] OK  {len(src)} élts avg={avg:.1f}")

    if corrupted:
        print(f"⚠  {len(corrupted)} cellule(s) corrompue(s) dans {path} :")
        for i, ctype, fmt, n, avg in corrupted:
            src = nb["cells"][i]["source"]
            preview = ("".join(src) if isinstance(src, list) else src)[:60].replace("\n", "↵")
            print(f"  cell-{i:02d} [{ctype}] format={fmt} {n} élts avg={avg:.1f}  {preview!r}")
        sys.exit(1)
    else:
        print(f"✓ {path} — aucune corruption détectée ({len(nb['cells'])} cellules)")


def main():
    p = argparse.ArgumentParser(description="Vérifier l'intégrité des sources d'un notebook")
    p.add_argument("notebook")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()
    check(args.notebook, args.verbose)


if __name__ == "__main__":
    main()
