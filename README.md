# Dagster flow

- collect homes.  New homes are added to the cache, with synced = false
- filter homes.  Using the search result, apply a filter on the spreadsheet to hide the homes that are no longer in 
  the results.
- score homes.  Score all the homes that have synced = false.
- sync homes.  Collect homes with synced = false and send them to spreadsheet.  Update synced=true when done.

# Data

- home_cache.db: sqlite database that holds the home cache (downloaded and scored homes)
- google spreadsheet with id "SPREADSHEET_ID": final destination for the scored homes

# Configuration

- .env: for configuration of secrets:
  - `MAPQUEST_API_KEY`
  - `SPREADSHEET_ID`, `SPREADSHEET_GID`: get those from the address bar
- pois.csv: configuration of points of interest for distance score.  They get updated with the geocode
- ops_config.yml: configuration of paths etc
- token.json: something that gets generated during initial connection to the Google Sheet API

# Running

Docker configuration in `docker` folder:

- Dockerfile.dagit: code container, runs the dagit interface

Right now you have to first generate the requirements.txt:

    poetry export --without-hashes > requirements.txt

And make sure that the version of dagit in the Dockerfile matches the 
version of dagster in pyproject.toml.