from contextlib import closing

import pandas as pd
from prefect import task

from localize_be.core.scoring import calculate_score
from localize_be.resources.home_cache import get_home_cache


@task()
def score_all(pois: pd.DataFrame):
    with closing(get_home_cache()) as home_cache:
        homes = home_cache.get_homes_to_sync()
        for id_, details in homes:
            calculate_score(details, pois)
            home_cache.update_home(id_, details)
