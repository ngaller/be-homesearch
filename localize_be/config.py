from dotenv import load_dotenv
from os import environ

load_dotenv()
config = {
    "HOME_CACHE": {
        "PATH": environ.get("HOME_CACHE__PATH") or "home_cache.db"
    },
    "SHEET": {
        "SPREADSHEET_ID": environ.get("SHEET__SPREADSHEET_ID"),
        "SPREADSHEET_GID": environ.get("SHEET__SPREADSHEET_GID"),
    }
}
