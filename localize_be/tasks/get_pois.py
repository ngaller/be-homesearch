"""
Collect pois from the pois.csv file and geocode them.
"""
import numpy as np
import pandas as pd
from dagster import op

from localize_be.resources.mapquest import Mapquest


@op(required_resource_keys={"mapquest"}, config_schema={"path": str})
def get_pois(context) -> pd.DataFrame:
    path = context.op_config["path"]
    mapquest: Mapquest = context.resources.mapquest
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
