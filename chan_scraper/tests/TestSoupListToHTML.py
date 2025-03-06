# Imports
import json

from bs4 import BeautifulSoup
from datetime import datetime

from ..src import HomepageURLRetriever
from ..src import SoupListToHTML
from ..src import URLListToSoupList

# Run as module to make relative import work:
# python -m chan_scraper.tests.TestSoupListToHTML

class TestSoupListToHTML: 
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

        soup_list: list[tuple[datetime, BeautifulSoup]] = URLListToSoupList.\
            url_list_to_soup_list(self.scan_time, url_list)

        SoupListToHTML.soup_list_to_html(
            soup_list,
            self.params_data["site_dir"], self.params_data["id_class"])

if __name__ == '__main__':
    test = TestSoupListToHTML()
    test.test_html_outputs()
