from dagster import job

from localize_be.ops import collect_homes, score_homes, sync, get_pois, geocode
from localize_be.resources.home_cache import home_cache
from localize_be.resources.immoweb import immoweb
from localize_be.resources.mapquest import mapquest
from localize_be.resources.sheet import sheet


@job(resource_defs={"mapquest": mapquest, "home_cache": home_cache, "immoweb": immoweb, "sheet": sheet})
def update_homes():
    search = collect_homes.search_homes()
    scraping = collect_homes.get_new_homes(search)
    geocoding = geocode.geocode_homes(start=scraping)
    pois = get_pois.get_pois()
    scoring = score_homes.score_all(pois, start=geocoding)
    sync.sync_new(start=scoring)
    sync.filter_old(search)
