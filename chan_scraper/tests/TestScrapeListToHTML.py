# Imports
import json

from bs4 import BeautifulSoup
from datetime import datetime

from ..src import HomepageURLRetriever
from ..src import ScrapeData
from ..src import ScrapeListToHTML
from ..src import URLListToScrapeList

# Run as module to make relative import work:
# python -m chan_scraper.tests.TestScrapeListToHTML

# Passes as of 2025-03-06

class TestScrapeListToHTML: 
    """Performs test with test directory on SoupListToHTML."""   
    def __init__(self):
        filepath_input = input("Enter params filepath \n")
        # Using ./data/params/tests/test_params.json right now
        self.filepath = filepath_input
        with open(self.filepath, "r") as params:
            self.params_data = json.load(params)
        self.scan_time = datetime.today()

    def test_html_outputs(self):
        homepage_url_retriever = HomepageURLRetriever(
            self.params_data["hp_url"], self.params_data["url"], 
            self.params_data["container"])
        url_list: list[str] = homepage_url_retriever.urls_to_list()

        scrapes: list[ScrapeData] = URLListToScrapeList.\
            url_list_to_scrape_list(self.scan_time, url_list)

        ScrapeListToHTML.scrape_list_to_html(
            scrapes,
            self.params_data["site_dir"])

if __name__ == '__main__':
    test = TestScrapeListToHTML()
    test.test_html_outputs()
