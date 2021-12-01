from dagster import op, Nothing, In

from localize_be.resources.home_cache import HomeCache
from localize_be.resources.mapquest import Mapquest


@op(required_resource_keys={"mapquest", "home_cache"}, ins={"start": In(Nothing)})
def geocode_homes(context):
    mapquest: Mapquest = context.resources.mapquest
    home_cache: HomeCache = context.resources.home_cache
    homes = home_cache.get_homes_to_geocode()
    for id_, home in homes:
        home["Lat"], home["Lng"] = mapquest.geocode(f"{home['Street']}, {home['City']}")
        home_cache.update_home(id_, home)
        home_cache.set_geocoded(id_)
