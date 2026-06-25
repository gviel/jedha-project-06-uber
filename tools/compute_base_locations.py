#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

input_dir = Path("data/uber-trip-data/2014")
output_file = Path("data/computed_base_locations_2014.csv")

results = []

for file in input_dir.glob("*.csv"):
    df = pd.read_csv(file)

    if df.shape[1] < 4:
        print(f"Fichier {file.name} ignoré (moins de 4 colonnes)")
        continue

    df = df.rename(columns={
        df.columns[1]: "Lat",
        df.columns[2]: "Lon",
        df.columns[3]: "Base"
    })

    grouped = df.groupby("Base").agg(
        Lat_Moy=("Lat", "mean"),
        Lon_Moy=("Lon", "mean"),
        Lat_Std=("Lat", "std"),
        Lon_Std=("Lon", "std")
    ).reset_index()

    results.append(grouped)

if results:
    final_df = pd.concat(results, ignore_index=True)
    final_df.to_csv(output_file, index=False)
    print(f"Coordonnées moyennes enregistrées dans {output_file}")
else:
    print("Aucun fichier CSV valide trouvé.")
