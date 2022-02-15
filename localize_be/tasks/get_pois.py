"""
Collect pois from the pois.csv file and geocode them.
"""
import numpy as np
import pandas as pd
from prefect import task

from localize_be.config import config
from localize_be.resources.mapquest import get_mapquest


@task()
def get_pois(path: str = None) -> pd.DataFrame:
    path = path or config["POIS"]["PATH"]
    mapquest = get_mapquest()
    df = pd.read_csv(path, sep=";")
    if "Lat" not in df.columns:
        df["Lat"], df["Lng"] = np.nan, np.nan

    def geocode(row):
        if np.isnan(row.Lat):
            return mapquest.geocode(row.Address)
        return row.Lat, row.Lng

    df["Lat"], df["Lng"] = zip(*df.apply(geocode, axis=1))
    df.to_csv(path, sep=";", index=False)
    return df
