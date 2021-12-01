from typing import Tuple

import requests
from dagster import resource, InitResourceContext, StringSource

COUNTRY = "Belgium"


class Mapquest:
    def __init__(self, api_key):
        self.api_key = api_key

    def geocode(self, address: str) -> Tuple[int, int]:
        """
        Return a tuple of lat, lng
        """
        r = requests.get("http://www.mapquestapi.com/geocoding/v1/address", params={
            "key": self.api_key,
            "location": f"{address}, {COUNTRY}",
            "maxResults": 1,
            "outFormat": "json"
        })
        r.raise_for_status()
        loc = r.json()["results"][0]["locations"][0]["latLng"]
        return loc["lat"], loc["lng"]


@resource(config_schema={"api_key": StringSource})
def mapquest(init_context: InitResourceContext):
    svc = Mapquest(init_context.resource_config["api_key"])
    return svc
