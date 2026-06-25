#!/usr/bin/env python3
"""nb_grep.py — rechercher un pattern dans les cellules d'un notebook.

Usage:
    python nb_grep.py notebook.ipynb "df_cleaned"
    python nb_grep.py notebook.ipynb "drop" --code
    python nb_grep.py notebook.ipynb "4\.\d\)" --md -i
"""
import json, argparse, re, sys


def grep(path, pattern, ignore_case=False, cell_filter=None):
    with open(path, encoding="utf-8") as f:
        nb = json.load(f)

    flags = re.IGNORECASE if ignore_case else 0
    try:
        regex = re.compile(pattern, flags)
    except re.error as e:
        print(f"Pattern regex invalide : {e}", file=sys.stderr)
        sys.exit(1)

    found = False
    for i, cell in enumerate(nb["cells"]):
        ctype = cell["cell_type"]
        if cell_filter and ctype != cell_filter:
            continue
        src = "".join(cell.get("source", []))
        for j, line in enumerate(src.split("\n")):
            if regex.search(line):
                tag = "code" if ctype == "code" else "md  "
                print(f"cell-{i:02d}:{j+1:3d}  [{tag}]  {line}")
                found = True

    if not found:
        print(f"Aucune occurrence de '{pattern}'.", file=sys.stderr)
        sys.exit(1)


def main():
    p = argparse.ArgumentParser(description="Grep dans les cellules d'un notebook")
    p.add_argument("notebook", help="chemin vers le .ipynb")
    p.add_argument("pattern", help="expression régulière à rechercher")
    p.add_argument("-i", "--ignore-case", action="store_true")
    p.add_argument("--code", action="store_true", help="seulement cellules code")
    p.add_argument("--md", action="store_true", help="seulement cellules markdown")
    args = p.parse_args()

    cell_filter = None
    if args.code:
        cell_filter = "code"
    elif args.md:
        cell_filter = "markdown"

    grep(args.notebook, args.pattern, args.ignore_case, cell_filter)


if __name__ == "__main__":
    main()
