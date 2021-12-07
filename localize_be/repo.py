from dagster import repository

from localize_be.jobs.fill_cache import fill_cache
from localize_be.jobs.update_homes import update_homes


@repository
def localize_be():
    return [
        fill_cache,
        update_homes
    ]
