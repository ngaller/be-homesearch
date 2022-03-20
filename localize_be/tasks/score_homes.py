from contextlib import closing

import pandas as pd
from prefect import task

from localize_be.config import logger
from localize_be.core.scoring import calculate_score
from localize_be.resources.home_cache import get_home_cache


@task()
def score_all(pois: pd.DataFrame, rescore: bool = False):
    with closing(get_home_cache()) as home_cache:
        homes = home_cache.get_homes_to_sync() if not rescore else home_cache.get_homes_geocoded()
        logger.debug(f"Scoring {len(homes)} homes")
        for id_, details in homes:
            try:
                calculate_score(details, pois)
                home_cache.update_home(id_, details)
            except Exception as e:
                logger.warning(f"Error updating score for home {id_}: {e}")
