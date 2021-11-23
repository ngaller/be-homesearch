all: refresh gsheet

refresh:
	touch .refresh

homes.csv: .refresh
	pipenv run python gather_homes.py homes.csv

homes_scored.csv: home_search.rmd homes.csv
	RSTUDIO_PANDOC=/usr/lib/rstudio/bin/pandoc Rscript -e "rmarkdown::render('home_search.rmd')"

gsheet: homes_scored.csv
	pipenv run python update_spreadsheet.py homes_scored.csv
