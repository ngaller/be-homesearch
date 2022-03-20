from localize_be.config import config
from localize_be.resources.mapquest import Mapquest


def test_geocode_simple():
    m = Mapquest(config["MAPQUEST"]["API_KEY"])
    ll = m.geocode("4 rue Doucet, 1370 Dongelberg")
    assert ll == (50.70128, 4.82279)


def test_geocode_by_city_with_zip():
    m = Mapquest(config["MAPQUEST"]["API_KEY"])
    ll = m.geocode("1360 MALÈVES-SAINTE-MARIE-WASTINNES")
    assert ll == (50.65833, 4.792)
