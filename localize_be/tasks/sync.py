from contextlib import closing
from typing import List

from prefect import task

from localize_be.resources.home_cache import get_home_cache
from localize_be.resources.sheet import get_sheet


@task()
def filter_old(exclude_homes: List[int]):
    """Apply filter on spreadsheet to show only houses that are in current search results"""
    if exclude_homes:
        get_sheet().set_home_filter(exclude_homes)


@task()
def sync_new():
    """Append new houses and mark as synced in home cache"""
    with closing(get_home_cache()) as cache:
        to_sync = cache.get_homes_to_sync()
        if to_sync:
            get_sheet().add_homes([d[1] for d in to_sync])
            for id_, _ in to_sync:
                cache.set_synced(id_)
        return len(to_sync)
