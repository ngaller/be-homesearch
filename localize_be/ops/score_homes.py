import pandas as pd
from dagster import op, OpExecutionContext, In, Nothing

from localize_be.core.scoring import calculate_score


@op(required_resource_keys={"home_cache"}, ins={"start": In(Nothing)})
def score_all(context: OpExecutionContext, pois: pd.DataFrame):
    home_cache = context.resources.home_cache
    homes = home_cache.get_homes_to_sync()
    for id_, details in homes:
        calculate_score(details, pois)
        home_cache.update_home(id_, details)
