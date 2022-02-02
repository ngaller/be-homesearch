from prefect import Flow

from localize_be.tasks import collect_homes, score_homes, sync, get_pois, geocode

with Flow("Update Homes") as flow:
    search = collect_homes.search_homes()
    scraping = collect_homes.get_new_homes(search)
    geocoding = geocode.geocode_homes()
    flow.add_edge(scraping, geocoding)
    pois = get_pois.get_pois()
    scoring = score_homes.score_all(pois)
    flow.add_edge(geocoding, scoring)
    sync_new = sync.sync_new()
    flow.add_edge(scoring, sync_new)
    sync.filter_old(collect_homes.get_old_homes(search))
