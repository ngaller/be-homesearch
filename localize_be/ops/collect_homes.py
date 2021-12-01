from typing import List, Dict

from dagster import op, AssetMaterialization, Output, Out
import pandas as pd
from dagster_pandas import create_dagster_pandas_dataframe_type, PandasColumn

HomeSearchDataframe = create_dagster_pandas_dataframe_type(
    name="HomeSearchDataframe",
    columns=[
        PandasColumn.string_column("city"),
        PandasColumn.string_column("postal_code"),
        PandasColumn.integer_column("price"),
    ]
)


@op(required_resource_keys={"immoweb"}, out=Out(HomeSearchDataframe))
def search_homes(context) -> pd.DataFrame:
    """Retrieve from immoweb"""
    # TODO pass configured search criteria somehow?
    df = pd.DataFrame(data=list(context.resources.immoweb.search_homes())).set_index("id")
    print(df)
    return df


@op(required_resource_keys={"immoweb", "home_cache"})
def get_new_homes(context, search_result: pd.DataFrame):
    """Get detailed information for the new houses"""
    count = 0
    for code, row in search_result.iterrows():
        if not context.resources.home_cache.has_home(code, row["price"]):
            details = context.resources.immoweb.get_home(code, row["city"], row["postal_code"])
            context.resources.home_cache.add_home({"id": code, **row}, details)
            yield AssetMaterialization(str(code), description=f"Property#{code}")
            count += 1
    yield Output(count)
