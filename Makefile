install: pyproject.toml
	poetry install

build: docker-compose.yaml
	docker-compose build

up: build
	docker-compose up -d

down:
	docker-compose down

register:
	PYTHONPATH=. poetry run prefect register --project localize_be \
		--module localize_be.flows.fill_cache.flow \
		--module localize_be.flows.update_homes.flow

#refresh:
#	touch .refresh
#
#homes.csv: .refresh
#	pipenv run python gather_homes.py homes.csv
#
#homes_scored.csv: home_search.rmd homes.csv
#	RSTUDIO_PANDOC=/usr/lib/rstudio/bin/pandoc Rscript -e "rmarkdown::render('home_search.rmd')"
#
#gsheet: homes_scored.csv
#	pipenv run python update_spreadsheet.py homes_scored.csv
