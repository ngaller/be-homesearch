from dotenv import load_dotenv
from os import environ

load_dotenv()
config = {
    "HOME_CACHE": {
        "PATH": environ.get("HOME_CACHE__PATH") or "db/home_cache"
    },
    "SHEET": {
        "SPREADSHEET_ID": environ.get("SHEET__SPREADSHEET_ID"),
        "SPREADSHEET_GID": environ.get("SHEET__SPREADSHEET_GID"),
    },
    "MAPQUEST": {
        "API_KEY": environ.get("MAPQUEST__API_KEY")
    },
    "POIS": {
        "PATH": environ.get("POIS__PATH") or "pois.csv"
    }
}
