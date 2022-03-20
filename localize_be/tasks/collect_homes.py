from contextlib import closing
from typing import List

import pandas as pd
from prefect import task

from localize_be.config import logger
from localize_be.resources.home_cache import get_home_cache
from localize_be.resources.immoweb import get_immoweb


@task()
def search_homes() -> pd.DataFrame:
    """Retrieve from immoweb"""
    # TODO pass configured search criteria somehow?
    api = get_immoweb()
    df = pd.DataFrame(data=list(api.search_homes()))
    return df


@task()
def get_new_homes(search_result: pd.DataFrame):
    """Get detailed information for the new houses (the ones that are not in cache yet)"""
    with closing(get_home_cache()) as cache:
        count = 0
        for _, row in search_result.iterrows():
            code = row.id
            if not cache.has_home(code, row["price"]):
                details = get_immoweb().get_home(code, row["property_type"], row["city"],
                                                 row["postal_code"])
                cache.add_home(row.to_dict(), details)
                count += 1
            else:
                print("Already has home", code)
        return count


@task()
def refetch_cached_homes():
    with closing(get_home_cache()) as cache:
        count = 0
        for row in cache.get_homes_missing_details():
            try:
                details = get_immoweb().get_home(row["id"],
                                                 row["property_type"] or "Home",
                                                 row["city"],
                                                 row["postal_code"])
                row["price"] = details["Price"]
                cache.add_home(row, details)
                count += 1
            except Exception as e:
                logger.warning(f"Could not fetch home {row['id']}: {e}")
    return count


@task()
def get_old_homes(search_result: pd.DataFrame) -> List[int]:
    """Get homes that are marked as synced in the cache but are no longer in the search results
    (thus those are the ones that need to be removed or hidden from the results)"""
    with closing(get_home_cache()) as cache:
        search_ids = set(search_result.id)
        return [x for x in cache.get_synced_ids() if x not in search_ids]
