import os.path

import pytest

from localize_be.resources.sheet import Sheet


@pytest.fixture
def svc():
    sheetid = "1z4jCjRgg8uPD-cVj7oIcN_pSRK4A1tVBNq3ErjhyTBo"
    sheetgid = "1068760068"
    return Sheet(sheetid, sheetgid,
                 os.path.join(os.path.dirname(__file__), ".."))


def test_get_homes(svc):
    homes = svc.get_homes()
    assert len(homes) > 10
    assert homes[0] == (0, {
        "id": 9477738,
        "postal_code": "1360",
        "price": 450000,
        "city": "Perwez",
        "property_type": "Home"
    })
    assert [h[0] for h in homes[0:10]] == list(range(10))


def test_update_homes(svc):
    result = svc.upsert_homes([{
        "Code #": 9365421,
        "Energy": "E"
    }])
    assert result == (0, 1)


def test_set_filter(svc):
    svc.set_home_filter([9461808])
