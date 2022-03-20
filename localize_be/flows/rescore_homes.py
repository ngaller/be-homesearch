from prefect import Flow

from localize_be.tasks import score_homes, sync, get_pois, geocode

with Flow("Rescore Homes") as flow:
    geocoding = geocode.geocode_homes()
    pois = get_pois.get_pois()
    scoring = score_homes.score_all(pois, rescore=True)
    flow.add_edge(geocoding, scoring)
    sync_new = sync.sync_new()
    flow.add_edge(scoring, sync_new)
