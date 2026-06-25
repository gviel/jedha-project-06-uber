#!/usr/bin/env python3
"""nb_inspect.py — liste toutes les cellules d'un notebook avec index et aperçu.

Usage:
    python nb_inspect.py notebook.ipynb
    python nb_inspect.py notebook.ipynb --code
    python nb_inspect.py notebook.ipynb --md
    python nb_inspect.py notebook.ipynb --headers
"""
import json, argparse, sys


def inspect(path, code_only=False, md_only=False, headers_only=False):
    with open(path, encoding="utf-8") as f:
        nb = json.load(f)
    cells = nb["cells"]

    n_code = n_md = 0
    for i, cell in enumerate(cells):
        ctype = cell["cell_type"]
        src = "".join(cell.get("source", []))
        lines = src.split("\n")

        if code_only and ctype != "code":
            continue
        if md_only and ctype != "markdown":
            continue

        if headers_only:
            if ctype != "markdown":
                continue
            header_lines = [l for l in lines if l.startswith("#")]
            if not header_lines:
                continue
            for hl in header_lines:
                print(f"cell-{i:02d}  {hl}")
            continue

        type_tag = "CODE" if ctype == "code" else "MD  "
        exec_count = cell.get("execution_count") or ""
        exec_str = f"[{exec_count}]" if exec_count else "    "
        first = lines[0][:80] if lines and lines[0].strip() else (lines[1][:80] if len(lines) > 1 else "")
        print(f"{i:3d}  {type_tag}  {exec_str:6s}  {len(lines):3d}L  {first!r}")

        if ctype == "code":
            n_code += 1
        else:
            n_md += 1

    if not headers_only:
        total = len(cells)
        print(f"\n{total} cellules total  ({n_code if not md_only else '?'} code, "
              f"{n_md if not code_only else '?'} markdown)")


def main():
    p = argparse.ArgumentParser(description="Lister les cellules d'un notebook Jupyter")
    p.add_argument("notebook", help="chemin vers le .ipynb")
    p.add_argument("--code", action="store_true", help="seulement les cellules code")
    p.add_argument("--md", action="store_true", help="seulement les cellules markdown")
    p.add_argument("--headers", action="store_true", help="seulement les titres markdown (#, ##, ###)")
    args = p.parse_args()
    inspect(args.notebook, code_only=args.code, md_only=args.md, headers_only=args.headers)


if __name__ == "__main__":
    main()
