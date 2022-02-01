"""
Fill local cache with the homes from Google sheet
"""
from contextlib import closing

import pandas as pd
from prefect import task

from localize_be.resources.sheet import sheet
from localize_be.resources.home_cache import home_cache


@task()
def add_to_cache(homes: pd.DataFrame):
    with closing(home_cache()) as cache:
        for _, h in homes.iterrows():
            cache.add_home(h.to_dict(), details={}, synced=True)


@task()
def get_homes():
    homes = sheet().get_homes()
    df = pd.DataFrame(data=[v[1] for v in homes])
    return df
