# Dagster flow

- collect homes.  New homes are added to the cache, with synced = false
- filter homes.  Using the search result, apply a filter on the spreadsheet to hide the homes that are no longer in 
  the results.
- score homes.  Score all the homes that have synced = false.
- sync homes.  Collect homes with synced = false and send them to spreadsheet.  Update synced=true when done.

# Data

- db/home_cache: sqlite database that holds the home cache (downloaded and scored homes)
- google spreadsheet with id "SPREADSHEET_ID": final destination for the scored homes

# Configuration

- .env: for configuration of secrets:
  - `MAPQUEST_API_KEY`
  - `SPREADSHEET_ID`, `SPREADSHEET_GID`: get those from the address bar
- pois.csv: configuration of points of interest for distance score.  They get updated with the geocode
- token.json: something that gets generated during initial connection to the Google Sheet API
- credentials.json: Google API credentials, saved from the site

# Running

Docker configuration in `docker` folder:

- Dockerfile: prefect agent

Runtime configuration is in the `.env` file.

Run the agent using docker-compose.  The `db` path must be accessible (rw) to the
user id in docker.

There are 2 flows:

- fill_cache is used to initialize the home_cache db using the values from 
  the spreadsheet
- update_homes searches immoweb and updates the spreadsheet with the homes
  that are missing from the cache