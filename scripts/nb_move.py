#!/usr/bin/env python3
"""nb_move.py — déplacer un bloc de cellules dans un notebook.

Usage:
    python nb_move.py notebook.ipynb 17:20 28        # cells 17-20 après cell-28
    python nb_move.py notebook.ipynb 5 12            # cell seule (5) après cell-12
    python nb_move.py notebook.ipynb 17:20 28 --dry-run
    python nb_move.py notebook.ipynb 17:20 28 --backup
"""
import json, argparse, shutil, sys
from pathlib import Path


def parse_range(spec, n_cells):
    if ":" in spec:
        parts = spec.split(":")
        return int(parts[0]), int(parts[1])
    idx = int(spec)
    return idx, idx


def move(path, start, end, after, dry_run=False, backup=False):
    with open(path, encoding="utf-8") as f:
        nb = json.load(f)
    cells = nb["cells"]
    n = len(cells)

    if start < 0 or end >= n or start > end:
        print(f"Plage {start}:{end} invalide (0–{n-1})", file=sys.stderr)
        sys.exit(1)
    if after < 0 or after >= n:
        print(f"Position after={after} hors limites (0–{n-1})", file=sys.stderr)
        sys.exit(1)
    if start <= after <= end:
        print(f"'after' ({after}) ne peut pas être dans le bloc déplacé ({start}:{end})", file=sys.stderr)
        sys.exit(1)

    block = cells[start : end + 1]
    rest  = cells[:start] + cells[end + 1:]

    # Recalculer insert_pos dans rest (après suppression du bloc)
    insert_after_adj = after if after < start else after - len(block)
    insert_pos = insert_after_adj + 1

    new_cells = rest[:insert_pos] + block + rest[insert_pos:]

    print(f"Déplacement cell-{start}:{end} ({len(block)} cellule(s)) → après cell-{after}")
    for i, cell in zip(range(start, end + 1), block):
        src = "".join(cell.get("source", []))
        preview = src[:60].replace("\n", " | ")
        print(f"  cell-{i}: {preview!r}")

    if dry_run:
        print("[dry-run] aucune modification")
        return

    if backup:
        bak = Path(path).with_suffix(".ipynb.bak")
        shutil.copy2(path, bak)
        print(f"Backup : {bak}")

    nb["cells"] = new_cells
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print("✓ Déplacement effectué")


def main():
    p = argparse.ArgumentParser(description="Déplacer un bloc de cellules dans un notebook")
    p.add_argument("notebook", help="chemin vers le .ipynb")
    p.add_argument("range", help="plage de cellules  ex: 17:20  ou cellule seule: 17")
    p.add_argument("after", type=int, help="insérer après la cellule N")
    p.add_argument("--dry-run", action="store_true", help="simulation sans écriture")
    p.add_argument("--backup", action="store_true", help="créer un .bak avant modification")
    args = p.parse_args()

    with open(args.notebook, encoding="utf-8") as f:
        n = len(json.load(f)["cells"])

    start, end = parse_range(args.range, n)
    move(args.notebook, start, end, args.after, args.dry_run, args.backup)


if __name__ == "__main__":
    main()
