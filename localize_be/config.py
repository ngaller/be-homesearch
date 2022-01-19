import os

from localize_be.resources.home_cache import HomeCache
from localize_be.resources.sheet import Sheet

config = {
    "HOME_CACHE": os.environ["HOME_CACHE"],
    "MAPQUEST_API_KEY": os.environ["MAPQUEST_API_KEY"],
    "POIS_PATH": os.environ["POIS_PATH"],
    "SPREADSHEET_ID": os.environ["SPREADSHEET_ID"],
    "SPREADSHEET_GID": os.environ["SPREADSHEET_GID"],
}


def home_cache():
    db = HomeCache(config["HOME_CACHE"])
    return db


def sheet():
    return Sheet(config["SPREADSHEET_ID"], config["SPREADSHEET_GID"])
