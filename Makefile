# General vars
MAIN = ./src/web_scraper/__main__.py
REPARSER = ./src/web_scraper/parse/Reparser.py
PORTION_RETRIEVER = ./src/web_scraper/portion/PortionRetriever.py
SITE_NAME ?=  # reflected in data subfolder name (i.e crystalcafe is named crystal.cafe in data)

# Portioning vars:
THREAD_PERCENTAGE ?= 10 # can be overwritten in command-line. i.e (make portion THREAD_PERCENTAGE = 15)
RANDOMIZE ?= 1 # sets randomization as true

# Scrapes new data, reparses old data, and outputs thread portions
all: setup scrape reparse portion

# Installs dependencies
setup:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "Dependencies installed."

# Scrapes and parses new data
scrape: test_all
	@echo "Scraping and parsing new data for $(SITE_NAME)..."
	python $(MAIN) $(SITE_NAME)
	@echo "Scraping and parsing complete!"

# Reparses existing data from their saved HTMLs
reparse: test_all
	ifeq ($(SITE_NAME),)
		@echo "No site name entered. Reparsing all data."
	else
		@echo "Reparsing all data for $(SITE_NAME)"
		
	python $(REPARSER) $(SITE_NAME)
	@echo "Reparsing complete!"

# Retrieves portions from all sites
portion: 
	@echo "Portioning threads"
	python $(PORTION_RETRIEVER) $(THREAD_PERCENTAGE) $(SITE_NAME) $(RANDOMIZE) 

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
	rm -rf ./data/thread_portion/crystal.cafe
	rm -rf ./data/thread_portion/wizchan
	@echo "Cleanup complete."      

.PHONY: run clean