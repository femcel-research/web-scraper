#file paths
CRYSTAL_MAIN = ./crystalcafe-scraper/main.py
WIZ_MAIN = ./wizchan-scraper/main.py 

#TODO: Simplify once scraper becomes modular
THREAD_PERCENTAGE = 10 #can be overwritten in command-line. i.e (make portion THREAD_PERCENTAGE = 15)

CC_PORTION_RETRIEVER = ./crystalcafe-scraper/utils/PortionRetriever.py
CC_SITE_NAME = crystal.cafe

WIZ_PORTION_RETRIEVER = ./wizchan-scraper/utils/PortionRetriever.py
WIZ_SITE_NAME = wizchan

# Installs dependencies
setup:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "Dependencies installed."

# Runs specific portion retrievers
cc_portion:
	python $(CC_PORTION_RETRIEVER) $(THREAD_PERCENTAGE) $(CC_SITE_NAME)
wiz_portion:
	python $(WIZ_PORTION_RETRIEVER) $(THREAD_PERCENTAGE) $(WIZ_SITE_NAME)

# Retrieves portions from all sites
portion: cc_portion wiz_portion

# Scrapes new data and outputs thread portions
all: run portion

# Runs specific scrapers
crystal:
	python $(CRYSTAL_MAIN)

wiz: 
	python $(WIZ_MAIN)

# Runs all scrapers
run: crystal wiz

clean:
	@echo "Cleaning up..."
	rm -rf __pycache__
	rm -rf ./data/thread_portion/crystal.cafe
	rm -rf ./data/thread_portion/wizchan
	@echo "Cleanup complete."      

.PHONY: run clean