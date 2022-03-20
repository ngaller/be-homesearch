from contextlib import closing

from prefect import task

from localize_be.resources.home_cache import get_home_cache
from localize_be.resources.mapquest import get_mapquest


@task()
def geocode_homes():
    mapquest = get_mapquest()
    with closing(get_home_cache()) as cache:
        homes = cache.get_homes_to_geocode()
        for id_, home in homes:
            home["Lat"], home["Lng"] = mapquest.geocode(f"{home['Street']}, {home['Postal code']} {home['City']}")
            cache.update_home(id_, home)
            cache.set_geocoded(id_)
