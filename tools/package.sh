#!/bin/bash
set -euo pipefail

readme="README.md"
presentation="docs/presentations/CDSD_bloc3_uber_GV.pdf"
output_dir="exports"
output_zip="${output_dir}/CDSD_bloc3_uber_GV_package.zip"

mkdir -p "${output_dir}"
rm -f "${output_zip}"

zip -j "${output_zip}" "${readme}" "${presentation}"

echo "Package créé : ${output_zip}"
