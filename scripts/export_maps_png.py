#!/usr/bin/env python3
"""export_maps_png.py — capture les figures Plotly HTML (exports/) en PNG via Chromium headless.

Les cartes mapbox/maplibre (scatter_map, Choroplethmapbox) ne sont pas exportables en PNG
via kaleido/fig.write_image() : les tuiles de fond chargées depuis un serveur externe (Carto,
OSM) souillent ("taint") le canvas WebGL, ce qui bloque toute lecture programmatique de ses
pixels (bouton appareil-photo Plotly, clic droit, kaleido...). Un vrai navigateur qui fait une
capture d'écran (compositeur, pas lecture JS du canvas) n'a pas cette restriction.

Usage:
    python scripts/export_maps_png.py                  # tous les exports/*.html
    python scripts/export_maps_png.py exports/2.6_*.html
    python scripts/export_maps_png.py --force           # regénère même si le .png est plus récent
"""
import argparse
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

TILE_LOAD_WAIT_MS = 2500  # laisse le temps aux tuiles de fond de carte de finir de charger


def export_one(page, html_path: Path, force: bool) -> bool:
    png_path = html_path.with_suffix(".png")
    if not force and png_path.exists() and png_path.stat().st_mtime >= html_path.stat().st_mtime:
        print(f"  skip (à jour) : {png_path.name}")
        return False

    page.goto(html_path.resolve().as_uri())
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(TILE_LOAD_WAIT_MS)

    plot_div = page.locator(".plotly-graph-div").first
    plot_div.screenshot(path=str(png_path))
    print(f"  ok : {png_path.name}")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*", help="fichiers .html à exporter (défaut : exports/*.html)")
    parser.add_argument("--force", action="store_true", help="regénère même si le .png est déjà à jour")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    if args.files:
        html_files = sorted(Path(f) for f in args.files)
    else:
        html_files = sorted((root / "exports").glob("*.html"))

    if not html_files:
        print("Aucun fichier .html trouvé.", file=sys.stderr)
        sys.exit(1)

    print(f"{len(html_files)} fichier(s) à traiter...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        n_done = 0
        for html_path in html_files:
            try:
                if export_one(page, html_path, args.force):
                    n_done += 1
            except Exception as e:
                print(f"  ERREUR sur {html_path.name} : {e}", file=sys.stderr)
        browser.close()

    print(f"Terminé : {n_done}/{len(html_files)} PNG générés.")


if __name__ == "__main__":
    main()
