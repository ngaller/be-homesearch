"""
Fill local cache with the homes from Google sheet
"""
import contextlib

import pandas as pd
from airflow.decorators import task

from localize_be import config
from localize_be.tasks.models.dataframes import HomeSearchDataframe


@task
def add_to_cache(homes: pd.DataFrame):
    with contextlib.closing(config.home_cache()) as cache:
        for _, h in homes.iterrows():
            cache.add_home(h.to_dict(), details={}, synced=True)


@task
def get_homes():
    homes = config.sheet().get_homes()
    df = pd.DataFrame(data=[v[1] for v in homes])
    return df
