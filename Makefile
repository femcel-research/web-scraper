# General vars
MAIN = ./src/web_scraper/__main__.py
REPARSER = ./src/web_scraper/parse/Reparser.py
SITE_META = src/web_scraper/parse/SiteMetaGenerator.py
PORTION_RETRIEVER = ./src/web_scraper/portion/PortionRetriever.py
SITE_NAME ?=# reflected in data subfolder name

# Portioning vars:
THREAD_PERCENTAGE ?= 10 # can be overwritten in command-line. i.e (make portion THREAD_PERCENTAGE = 15)
PORTION_DIRECTORY ?= ./data/portions
# RANDOMIZE ?= 1 # sets randomization as true

# Scrapes new data, reparses old data
all: setup test_all reparse scrape calculate_sitewide

# Installs dependencies
setup:
	@echo "Installing dependencies..."
#	pip install -r requirements.txt
	pip install .
	@echo "Dependencies installed."

# Scrapes and parses new data for a specified site
scrape: test_fetch test_scrape test_parse 
ifeq ($(SITE_NAME),)
	@echo "Scraping and parsing new data for all availiable sites"
	python $(MAIN)
	@echo "Scraping and parsing complete!"
else
	@echo "Scraping and parsing new data for $(SITE_NAME)..."
	python $(MAIN) $(SITE_NAME)
	@echo "Scraping and parsing complete!"
endif
	
# Reparses existing data from their saved HTMLs
reparse: test_parse 
ifeq ($(SITE_NAME),)
	@echo "No site name entered. Reparsing all data..."
	PYTHONPATH=./src python -m web_scraper.parse.Reparser
else
	@echo "Reparsing data for $(SITE_NAME)..."
	PYTHONPATH=./src python -m web_scraper.parse.Reparser $(SITE_NAME)
	@echo "Reparsing complete!"
endif

# # Retrieves portions, currently requires a site name
# portion: 
# 	@echo "Portioning threads..."
# 	python $(PORTION_RETRIEVER) $(THREAD_PERCENTAGE) $(SITE_NAME) $(RANDOMIZE)
# 	@echo "Portioning complete!"

portion:
	@echo "Portioning threads..."
	PYTHONPATH=./src python -m web_scraper.portion.portion $(THREAD_PERCENTAGE) $(PORTION_DIRECTORY) $(SITE_NAME)
	@echo "Portioning complete!"

# Calculates sitewide stats
calculate_sitewide:
ifeq ($(SITE_NAME),)
	@echo "No site name entered. Calculating stats for all sites..."
	python $(SITE_META) 
	@echo "Calculations complete!"
else
	@echo "Calculating stats data for $(SITE_NAME)..."
	python $(SITE_META) $(SITE_NAME)
	@echo "Calculations complete!"
endif

# Testing
test_all:
	@echo "Running automatic tests..."
	pytest 
	@echo "Tests complete!"

test_fetch:
	@echo "Running fetching tests..."
	pytest ./tests/test_fetch
	@echo "Tests complete!"

test_parse:
	@echo "Running parsing tests..."
	pytest ./tests/test_parse
	@echo "Tests complete!"

test_scrape:
	@echo "Running scraping tests..."
	pytest ./tests/test_scrape
	@echo "Tests complete!"

clean:
	@echo "Cleaning up..."
	rm -rf __pycache__
	rm -rf ./data/thread_portion/*
	@echo "Cleanup complete."      

.PHONY: run clean