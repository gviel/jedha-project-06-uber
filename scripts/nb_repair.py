#!/usr/bin/env python3
"""nb_repair.py — réparer les cellules dont le source est corrompu (char-par-char).

Deux types de corruption gérés :
  - source = string Python (stockée telle quelle au lieu d'une liste de lignes)
  - source = liste de 1 ou 2 chars par élément (ex: ['a\\n', 'b\\n', ...])

Usage:
    python scripts/nb_repair.py Uber_GV.ipynb           # aperçu (dry-run)
    python scripts/nb_repair.py Uber_GV.ipynb --fix     # correction en place
    python scripts/nb_repair.py Uber_GV.ipynb --fix --backup
"""
import json, argparse, shutil, sys
from pathlib import Path


def text_to_source(text: str) -> list:
    lines = text.split("\n")
    src = [l + "\n" for l in lines[:-1]]
    if lines[-1]:
        src.append(lines[-1])
    return src


def reconstruct(src) -> str:
    """Reconstruit le texte original depuis une source corrompue."""
    if isinstance(src, str):
        return src
    raw = "".join(src)
    avg = sum(len(s) for s in src) / len(src)
    if avg <= 2.1:
        # Chaque élément = char + '\n' parasite → prendre un char sur deux
        # mais les vrais '\n' sont stockés comme '\n\n' → [::2] ok
        return raw[::2]
    return raw


def repair(path, fix=False, backup=False, verbose=False):
    with open(path, encoding="utf-8") as f:
        nb = json.load(f)

    to_fix = []
    for i, cell in enumerate(nb["cells"]):
        src = cell.get("source", [])
        if not src:
            continue
        corrupted = False
        if isinstance(src, str) and len(src) > 10:
            corrupted = True
        elif isinstance(src, list) and len(src) > 5:
            avg = sum(len(s) for s in src) / len(src)
            if avg <= 2.1:
                corrupted = True
        if corrupted:
            to_fix.append(i)

    if not to_fix:
        print(f"✓ {path} — aucune corruption à réparer")
        return

    print(f"{'Réparation' if fix else 'Aperçu'} de {len(to_fix)} cellule(s) :")
    for i in to_fix:
        src = nb["cells"][i]["source"]
        text = reconstruct(src)
        new_src = text_to_source(text)
        preview = text[:80].replace("\n", "↵")
        print(f"  cell-{i:02d}: {len(src)} élts → {len(new_src)} lignes  {preview!r}")
        if fix:
            nb["cells"][i]["source"] = new_src

    if fix:
        if backup:
            bak = Path(path).with_suffix(".ipynb.bak")
            shutil.copy2(path, bak)
            print(f"Backup : {bak}")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(nb, f, ensure_ascii=False, indent=1)
        print(f"✓ {path} corrigé")
    else:
        print("(dry-run — relancer avec --fix pour appliquer)")


def main():
    p = argparse.ArgumentParser(description="Réparer les sources corrompues d'un notebook")
    p.add_argument("notebook")
    p.add_argument("--fix", action="store_true", help="appliquer la correction (défaut: dry-run)")
    p.add_argument("--backup", action="store_true", help="créer un .bak avant modification")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()
    repair(args.notebook, args.fix, args.backup, args.verbose)


if __name__ == "__main__":
    main()
