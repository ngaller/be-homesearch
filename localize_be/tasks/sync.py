from contextlib import closing
from typing import List

from prefect import task

from localize_be.config import logger
from localize_be.resources.home_cache import get_home_cache
from localize_be.resources.sheet import get_sheet


@task()
def filter_old(exclude_homes: List[int]):
    """Apply filter on spreadsheet to show only houses that are in current search results"""
    if exclude_homes:
        get_sheet().set_home_filter(exclude_homes)


@task()
def sync_new():
    """Sync newly added and updated houses and mark as synced in home cache"""
    with closing(get_home_cache()) as cache:
        to_sync = cache.get_homes_to_sync()
        if to_sync:
            logger.debug(f"Syncing {len(to_sync)} homes")
            get_sheet().upsert_homes([d[1] for d in to_sync])
            for id_, _ in to_sync:
                cache.set_synced(id_)
        else:
            logger.debug("No home to sync")
        return len(to_sync)
