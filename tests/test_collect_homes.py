import tempfile
from unittest.mock import MagicMock, patch

import pandas as pd

from localize_be.tasks.collect_homes import search_homes, get_new_homes, get_old_homes

# def test_read_existing():
#     context = build_op_context(op_config={"path": "samples/homes.csv"})
#     df = read_existing(context)
#     assert df is not None
#     assert df.loc[9627018] is not None
#     assert int(df.loc[9627018].Price) == 299000
from localize_be.resources.home_cache import HomeCache

SAMPLE_HOME = {"id": 9627018, "property_type": "Home", "city": "Lasnes", "postal_code": "1300", "price": 400000}


def test_search_homes():
    mock_immo = MagicMock()
    mock_immo.search_homes.return_value = [
        SAMPLE_HOME
    ]
    with patch("localize_be.tasks.collect_homes.get_immoweb") as get_immoweb:
        get_immoweb.return_value = mock_immo
        df = search_homes.run()
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
    with tempfile.NamedTemporaryFile() as f:
        local_cache = HomeCache(f.name)
        local_cache.add_home(SAMPLE_HOME, {}, synced=True)
        local_cache.set_geocoded(SAMPLE_HOME["id"])
        assert len(local_cache.get_homes_to_sync()) == 0
        df_search = pd.DataFrame(data=[
            SAMPLE_HOME,
            {"id": 111, "city": "Lasnes", "postal_code": "1234", "price": 4444},
        ])
        with patch("localize_be.tasks.collect_homes.get_immoweb") as get_immoweb, patch(
                "localize_be.tasks.collect_homes.get_home_cache") as get_cache:
            get_immoweb.return_value = mock_immo
            get_cache.return_value = local_cache
            result = get_new_homes.run(df_search)
        assert result == 1, "Should find only one new home, since SAMPLE_HOME was already in cache"
        local_cache = HomeCache(f.name)
        local_cache.set_geocoded(111)
        assert len(local_cache.get_homes_to_sync()) == 1, "Only new home should be set to sync"


def test_get_old_homes():
    local_cache = HomeCache(":memory:")
    local_cache.add_home(SAMPLE_HOME, {}, synced=True)
    df_search = pd.DataFrame(data=[
        {"id": 111, "city": "Lasnes", "postal_code": "1234", "price": 4444},
    ])
    with patch("localize_be.tasks.collect_homes.get_home_cache") as get_cache:
        get_cache.return_value = local_cache
        assert get_old_homes.run(df_search) == [SAMPLE_HOME["id"]]
