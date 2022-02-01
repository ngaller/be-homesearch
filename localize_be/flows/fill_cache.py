from prefect import Flow

from localize_be.tasks import fill_cache

with Flow('Fill Cache') as flow:
    homes = fill_cache.get_homes()
    fill_cache.add_to_cache(homes)
