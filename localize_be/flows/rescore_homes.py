from prefect import Flow

from localize_be.tasks import score_homes, sync, get_pois

with Flow("Rescore Homes") as flow:
    pois = get_pois.get_pois()
    scoring = score_homes.score_all(pois, rescore=True)
    sync_new = sync.sync_new()
    flow.add_edge(scoring, sync_new)
