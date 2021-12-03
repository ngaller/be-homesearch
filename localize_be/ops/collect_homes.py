from typing import List

from dagster import op, AssetMaterialization, Output, Out
import pandas as pd

from localize_be.ops.models.dataframes import HomeSearchDataframe


@op(required_resource_keys={"immoweb"}, out=Out(HomeSearchDataframe))
def search_homes(context) -> pd.DataFrame:
    """Retrieve from immoweb"""
    # TODO pass configured search criteria somehow?
    df = pd.DataFrame(data=list(context.resources.immoweb.search_homes()))
    print(df)
    return df


@op(required_resource_keys={"immoweb", "home_cache"})
def get_new_homes(context, search_result: pd.DataFrame):
    """Get detailed information for the new houses"""
    count = 0
    for _, row in search_result.iterrows():
        code = row.id
        if not context.resources.home_cache.has_home(code, row["price"]):
            details = context.resources.immoweb.get_home(code, row["city"], row["postal_code"])
            context.resources.home_cache.add_home(row.to_dict(), details)
            yield AssetMaterialization(str(code), description=f"Property#{code}")
            count += 1
        else:
            print("Already has home", code)
    yield Output(count)


@op(required_resource_keys={"home_cache"})
def get_old_homes(context, search_result: pd.DataFrame) -> List[int]:
    """Get homes that are marked as synced in the cache but are no longer in the search results"""
    search_ids = set(search_result.id)
    return [x for x in context.resources.home_cache.get_synced_ids() if x not in search_ids]
