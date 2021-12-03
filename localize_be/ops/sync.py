from typing import List

import pandas as pd
from dagster import op, Nothing, In

from localize_be.resources.home_cache import HomeCache
from localize_be.resources.sheet import Sheet


@op(required_resource_keys={"sheet"})
def filter_old(context, exclude_homes: List[int]):
    """Apply filter on spreadsheet to show only houses that are in current search results"""
    sheet: Sheet = context.resources.sheet
    if exclude_homes:
        sheet.set_home_filter(exclude_homes)


@op(required_resource_keys={"home_cache", "sheet"}, ins={"start": In(Nothing)})
def sync_new(context):
    """Append new houses and mark as synced in home cache"""
    home_cache: HomeCache = context.resources.home_cache
    sheet: Sheet = context.resources.sheet
    to_sync = home_cache.get_homes_to_sync()
    if to_sync:
        sheet.add_homes([d[1] for d in to_sync])
        for id_, _ in to_sync:
            home_cache.set_synced(id_)
    return len(to_sync)
