#!/usr/bin/env bash
# Ré-exécute le notebook et exporte les graphes PNG dans exports/
set -e

NOTEBOOK="Uber_GV.ipynb"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$ROOT"

echo "Exécution du notebook : $NOTEBOOK"
jupyter nbconvert --to notebook --execute "$NOTEBOOK" --output "$NOTEBOOK" --ExecutePreprocessor.timeout=300

echo "Graphes exportés dans exports/"
ls -lh exports/*.png 2>/dev/null || echo "(aucun PNG trouvé — vérifier que kaleido est installé)"
