from prefect import Flow
from prefect.tasks.prefect import create_flow_run

from localize_be.tasks.collect_homes import refetch_cached_homes

with Flow("Refetch Homes") as flow:
    refetch = refetch_cached_homes()
    flow_run = create_flow_run(flow_name="Rescore Homes",
                               project_name="localize-be")
    flow.add_edge(refetch, flow_run)
