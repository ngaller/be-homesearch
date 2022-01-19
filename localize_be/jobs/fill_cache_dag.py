from airflow.decorators import dag

from localize_be.tasks import fill_cache
from localize_be.resources.home_cache import home_cache
from localize_be.resources.sheet import sheet


@job(resource_defs={"home_cache": home_cache, "sheet": sheet})
def fill_cache():
    fill_cache.add_to_cache(fill_cache.get_homes())


@dag
def fill_cache():
    homes = fill_cache.get_homes()
    fill_cache.add_to_cache(homes)


job = fill_cache()
