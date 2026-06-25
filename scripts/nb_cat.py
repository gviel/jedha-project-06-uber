#!/usr/bin/env python3
"""nb_cat.py — afficher le contenu complet d'une ou plusieurs cellules.

Usage:
    python nb_cat.py notebook.ipynb 12
    python nb_cat.py notebook.ipynb 12 15 20
    python nb_cat.py notebook.ipynb 12:16          # plage inclusive
    python nb_cat.py notebook.ipynb 12 -o          # avec outputs
"""
import json, argparse, sys


def parse_specs(specs, n_cells):
    """Transforme ['5', '10:15', '20'] en liste d'indices."""
    indices = []
    for spec in specs:
        if ":" in spec:
            parts = spec.split(":")
            start = int(parts[0]) if parts[0] else 0
            end   = int(parts[1]) if parts[1] else n_cells - 1
            indices.extend(range(start, end + 1))
        else:
            indices.append(int(spec))
    return indices


def format_output(out):
    otype = out.get("output_type", "")
    if otype == "stream":
        text = "".join(out.get("text", []))
        return text[:1000] + ("…" if len(text) > 1000 else "")
    if otype in ("display_data", "execute_result"):
        data = out.get("data", {})
        if "text/plain" in data:
            txt = "".join(data["text/plain"])
            return txt[:1000] + ("…" if len(txt) > 1000 else "")
    return f"[{otype}]"


def cat(path, cell_specs, show_outputs=False):
    with open(path, encoding="utf-8") as f:
        nb = json.load(f)
    cells = nb["cells"]
    n = len(cells)

    indices = parse_specs(cell_specs, n)
    sep = "=" * 64

    for i in indices:
        if i < 0 or i >= n:
            print(f"# [ERREUR] cell-{i} hors limites (0–{n-1})", file=sys.stderr)
            continue
        cell = cells[i]
        ctype = cell["cell_type"]
        src = "".join(cell.get("source", []))
        exec_count = cell.get("execution_count", "–")

        print(sep)
        if ctype == "code":
            print(f"# cell-{i}  [code]  exec={exec_count}")
        else:
            print(f"# cell-{i}  [markdown]")
        print(sep)
        print(src)

        if show_outputs and ctype == "code":
            outputs = cell.get("outputs", [])
            if outputs:
                print(f"\n# ── outputs ({len(outputs)}) ──")
                for out in outputs:
                    print(format_output(out))
        print()


def main():
    p = argparse.ArgumentParser(description="Afficher le contenu de cellules d'un notebook")
    p.add_argument("notebook", help="chemin vers le .ipynb")
    p.add_argument("cells", nargs="+", help="indices ou plages  ex: 5   5:10   3 7 12")
    p.add_argument("-o", "--outputs", action="store_true", help="afficher les outputs")
    args = p.parse_args()
    cat(args.notebook, args.cells, args.outputs)


if __name__ == "__main__":
    main()
