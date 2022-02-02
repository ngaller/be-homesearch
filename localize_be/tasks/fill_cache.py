"""
Fill local cache with the homes from Google sheet
"""
from contextlib import closing

import pandas as pd
from prefect import task, context

from localize_be.resources.sheet import get_sheet
from localize_be.resources.home_cache import get_home_cache


@task()
def add_to_cache(homes: pd.DataFrame):
    context.logger.debug("add_to_cache: starting task execution")
    with closing(get_home_cache()) as cache:
        for _, h in homes.iterrows():
            cache.add_home(h.to_dict(), details={}, synced=True)


@task()
def get_homes():
    context.logger.debug("get_homes: starting task execution")
    homes = get_sheet().get_homes()
    df = pd.DataFrame(data=[v[1] for v in homes])
    context.logger.debug("get_homes: finished task execution")
    return df
