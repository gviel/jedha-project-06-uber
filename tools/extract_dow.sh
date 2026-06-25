#!/bin/bash
# Extrait les trajets par jour de la semaine depuis les CSV 2014.
# Produit 7 fichiers dans data/uber-trip-data/ : Lundi.csv ... Dimanche.csv
# A exécuter depuis la racine du projet.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/../data/uber-trip-data/2014"

echo "Création des fichiers pour chaque jour de la semaine..."
for day in Lundi Mardi Mercredi Jeudi Vendredi Samedi Dimanche; do
    touch "../$day.csv"
done
echo "Fichiers créés : Lundi, Mardi, Mercredi, Jeudi, Vendredi, Samedi, Dimanche."

for file in *.csv; do
    echo "Traitement du fichier : $file"

    while IFS=, read -r date lat lon base; do
        if [[ "$date" == "Date/Time" ]]; then
            continue
        fi

        if [[ "$date" =~ ([0-9]+)/([0-9]+)/([0-9]+)\ ([0-9]+):([0-9]+):([0-9]+) ]]; then
            month="${BASH_REMATCH[1]}"
            day="${BASH_REMATCH[2]}"
            year="${BASH_REMATCH[3]}"
            hour="${BASH_REMATCH[4]}"
            minute="${BASH_REMATCH[5]}"
            second="${BASH_REMATCH[6]}"

            reformatted_date="$year-$month-$day $hour:$minute:$second"
            day_of_week=$(date -d "$reformatted_date" +%u 2>/dev/null)

            if [ $? -eq 0 ]; then
                if [ "$day_of_week" -eq 7 ]; then
                    day_of_week=0
                fi

                case $day_of_week in
                    0) day_name="Dimanche" ;;
                    1) day_name="Lundi" ;;
                    2) day_name="Mardi" ;;
                    3) day_name="Mercredi" ;;
                    4) day_name="Jeudi" ;;
                    5) day_name="Vendredi" ;;
                    6) day_name="Samedi" ;;
                esac

                if [ "$day_name" ]; then
                    echo "$date,$lat,$lon,$base" >> "../$day_name.csv"
                fi
            fi
        fi
    done < "$file"
    echo "Traitement terminé pour le fichier : $file"
done

echo "Traitement complet."
