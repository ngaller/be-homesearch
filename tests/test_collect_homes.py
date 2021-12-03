from unittest.mock import MagicMock

import pandas as pd
from dagster import build_op_context, AssetMaterialization, Output

from localize_be.ops.collect_homes import search_homes, get_new_homes, get_old_homes

# def test_read_existing():
#     context = build_op_context(op_config={"path": "samples/homes.csv"})
#     df = read_existing(context)
#     assert df is not None
#     assert df.loc[9627018] is not None
#     assert int(df.loc[9627018].Price) == 299000
from localize_be.resources.home_cache import HomeCache

SAMPLE_HOME = {"id": 9627018, "city": "Lasnes", "postal_code": "1300", "price": 400000}


def test_search_homes():
    mock_immo = MagicMock()
    mock_immo.search_homes.return_value = [
        SAMPLE_HOME
    ]
    context = build_op_context(resources={
        "immoweb": mock_immo
    })
    df = search_homes(context)
    assert df is not None
    df = df.set_index("id")
    assert df.loc[9627018] is not None
    assert df.loc[9627018].city == "Lasnes"


def test_get_new_homes():
    mock_immo = MagicMock()
    mock_immo.get_home.return_value = {
        "Code #": 111,
        "Postal Code": "1233"
    }
    local_cache = HomeCache(":memory:")
    local_cache.add_home(SAMPLE_HOME, {}, synced=True)
    local_cache.set_geocoded(SAMPLE_HOME["id"])
    assert len(local_cache.get_homes_to_sync()) == 0
    context = build_op_context(resources={
        "immoweb": mock_immo,
        "home_cache": local_cache
    })
    df_search = pd.DataFrame(data=[
        SAMPLE_HOME,
        {"id": 111, "city": "Lasnes", "postal_code": "1234", "price": 4444},
    ])
    result = list(get_new_homes(context, df_search))
    assert isinstance(result[0], AssetMaterialization)
    assert isinstance(result[1], Output)
    assert result[1].value == 1
    local_cache.set_geocoded(111)
    assert len(local_cache.get_homes_to_sync()) == 1


def test_get_old_homes():
    local_cache = HomeCache(":memory:")
    local_cache.add_home(SAMPLE_HOME, {}, synced=True)
    context = build_op_context(resources={
        "home_cache": local_cache
    })
    df_search = pd.DataFrame(data=[
        {"id": 111, "city": "Lasnes", "postal_code": "1234", "price": 4444},
    ])
    assert get_old_homes(context, df_search) == [SAMPLE_HOME["id"]]
