#!/usr/bin/env python3
"""prepare_data.py — Prépare le dataset pour le dashboard Streamlit.

Charge les CSV Uber 2014, filtre sur les 2 premières semaines de septembre,
ajoute les colonnes temporelles, sauvegarde en parquet et pousse sur S3.

Usage (depuis la racine du projet) :
    conda run -n uber python dashboard/prepare_data.py
"""
import os
import time
from pathlib import Path
from joblib import Parallel, delayed

import boto3
import pandas as pd
from dotenv import load_dotenv

# Charge .env à la racine du projet (ignoré si absent)
load_dotenv(Path(__file__).parent.parent / ".env")

INPUT_DIR   = Path("data/uber-trip-data/2014")
OUTPUT_PATH = Path(__file__).parent / "dashboard_sept2w.parquet"

S3_BUCKET = os.environ.get("S3_BUCKET", "cdsd-uber-data")
S3_KEY    = "dashboard_sept2w.parquet"
S3_REGION = os.environ.get("AWS_DEFAULT_REGION", "eu-west-3")


def load_csv_uber(file: Path) -> pd.DataFrame:
    df = pd.read_csv(file, parse_dates=[0],
                     date_format={"Date/Time": "%m/%d/%Y %H:%M:%S"})
    df.rename(columns={k: c.replace("/", "").lower()
                        for k, c in zip(df.columns, df.columns)}, inplace=True)
    return df


def main():
    print(f"Chargement des CSV depuis {INPUT_DIR} …")
    file_list = sorted(INPUT_DIR.glob("*.csv"))
    if not file_list:
        raise FileNotFoundError(f"Aucun CSV trouvé dans {INPUT_DIR}")

    t0 = time.time()
    df_list = Parallel(n_jobs=6, backend="loky")(
        delayed(load_csv_uber)(f) for f in file_list
    )
    df = pd.concat(df_list, ignore_index=True)
    print(f"Chargé {len(df):,} lignes en {time.time()-t0:.1f}s")

    # Colonnes temporelles (mêmes conventions que le notebook)
    df["month"]    = df["datetime"].dt.strftime("%m")
    df["day"]      = df["datetime"].dt.strftime("%d")
    df["hour"]     = df["datetime"].dt.strftime("%H")
    df["dow"]      = df["datetime"].dt.strftime("%u").astype(int)  # 1=Lun … 7=Dim
    df["dow_name"] = df["datetime"].dt.day_name(locale="fr_FR.UTF-8")

    # Filtre : septembre, jours 1–14 (2 premières semaines)
    df = df[(df["month"] == "09") & (df["day"].astype(int) <= 14)].copy()
    df = df.drop(columns=["datetime"]).reset_index(drop=True)

    print(f"Dataset filtrés : {len(df):,} points")
    print(f"  Jours  : {sorted(df['dow'].unique())}  (1=Lun … 7=Dim)")
    print(f"  Heures : {df['hour'].min()} → {df['hour'].max()}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT_PATH, index=False)
    size_mb = OUTPUT_PATH.stat().st_size / 1e6
    print(f"✓ Sauvegardé : {OUTPUT_PATH}  ({size_mb:.1f} Mo)")

    # Upload S3
    print(f"Upload vers s3://{S3_BUCKET}/{S3_KEY} ({S3_REGION}) …")
    s3 = boto3.client("s3", region_name=S3_REGION)
    s3.upload_file(str(OUTPUT_PATH), S3_BUCKET, S3_KEY)
    print(f"✓ Disponible : s3://{S3_BUCKET}/{S3_KEY}")


if __name__ == "__main__":
    main()
