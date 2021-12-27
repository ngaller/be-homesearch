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

Make sure that the version of dagit in the Dockerfile matches the 
version of dagster in pyproject.toml.
The configuration has to be supplied manually in the launchpad.  I'm not
sure that it brings anything to use dagster resource configuration for this,
maybe we should just use environment variables.

There are 2 jobs:

- fill_cache is used to initialize the home_cache db using the values from 
  the spreadsheet
- update_homes searches immoweb and updates the spreadsheet with the homes
  that are missing from the cache