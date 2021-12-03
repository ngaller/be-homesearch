from dagster import job

from localize_be.ops import fill_cache
from localize_be.resources.home_cache import home_cache
from localize_be.resources.sheet import sheet


@job(resource_defs={"home_cache": home_cache, "sheet": sheet})
def fill_cache():
    fill_cache.fill_cache(fill_cache.get_homes())
