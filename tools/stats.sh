#!/bin/bash

declare -A monthnum=(
  [jan]=01 [feb]=02 [mar]=03 [apr]=04 [may]=05 [jun]=06
  [jul]=07 [aug]=08 [sep]=09 [oct]=10 [nov]=11 [dec]=12
)

data_dir="data/uber-trip-data"
output_file="data/stats_by_month.csv"

tmpfile=$(mktemp)
echo "year,month,nlines" > "${output_file}"

# fichiers 2014 par mois
echo "Traitement fichiers 2014..."
files=$(ls -1 ${data_dir}/2014/*.csv)
for f in $files; do
    n_lines=$(wc -l $f | cut -d' ' -f 1)
    let n_lines-- # pour supprimer le comptage de la ligne de header
    if [[ "$f" =~ ^data/uber-trip-data/([0-9]{4})/uber-raw-data-([a-z]+)[0-9]+\.csv$ ]]; then
        year="${BASH_REMATCH[1]}"
        month="${BASH_REMATCH[2]}"
        echo "Mois: ${month}"
        echo -e "${year},${monthnum[$month]},${n_lines}" >> "${tmpfile}"
    fi
done

# fichier 2015 contenant
echo "Traitement fichiers 2015..."
for i in $(seq -w 1 12); do
    echo "Mois: ${i}"
    n_lines=$(cat ${data_dir}/2015/*.csv | grep "2015-${i}" | wc -l)
    let n_lines-- # pour supprimer le comptage de la ligne de header
    if [[ $n_lines -gt 0 ]]; then
        echo -e "2015,${i},${n_lines}" >> "${tmpfile}"
    fi
done

cat "${tmpfile}" | sort >> "${output_file}"
rm "${tmpfile}"
