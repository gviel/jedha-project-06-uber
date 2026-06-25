#!/usr/bin/env python3
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

df = pd.read_csv("data/uber-trip-data/taxi-zone-lookup.csv")
print(df.head())

geolocator = Nominatim(user_agent="nyc_tlc_geocoder")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

df["search_query"] = df["Zone"] + ", " + df["Borough"] + ", New York City, USA"

latitudes = []
longitudes = []

for query in df["search_query"]:
    try:
        location = geocode(query)
        if location:
            latitudes.append(location.latitude)
            longitudes.append(location.longitude)
        else:
            latitudes.append(None)
            longitudes.append(None)
    except Exception as e:
        print(f"Erreur pour {query}: {e}")
        latitudes.append(None)
        longitudes.append(None)
    time.sleep(1)

df["latitude"] = latitudes
df["longitude"] = longitudes

df.to_csv("data/taxi-zone-geocoded.csv", index=False)
print("Geocodage termine. Fichier sauvegarde sous 'data/taxi-zone-geocoded.csv'")
