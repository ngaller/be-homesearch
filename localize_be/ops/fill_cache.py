"""
Fill local cache with the homes from Google sheet
"""
import pandas as pd
from dagster import op, Out

from localize_be.ops.models.dataframes import HomeSearchDataframe


@op(required_resource_keys={"home_cache"})
def add_to_cache(context, homes: pd.DataFrame):
    for _, h in homes.iterrows():
        context.resources.home_cache.add_home(h.to_dict(), details={}, synced=True)


@op(required_resource_keys={"sheet"}, out=Out(HomeSearchDataframe))
def get_homes(context):
    homes = context.resources.sheet.get_homes()
    df = pd.DataFrame(data=[v[1] for v in homes])
    return df
