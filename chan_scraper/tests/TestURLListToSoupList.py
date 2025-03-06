# Imports
import json

from datetime import datetime

from ..src import HomepageURLRetriever
from ..src import URLListToSoupList

# Run as module to make relative import work:
# python -m chan_scraper.tests.TestURLListToSoupList

class TestURLListToSoupList: 
    """Performs visual tests with prints on URLListToSoupList.

    Uses BeautifulSoup object title string outputs and
    datetime strftime outputs for confirmation.
    """   
    def __init__(self):
        filepath_input = input("Enter params filepath \n")
        # Using ./data/params/tests/test_params.json right now
        self.filepath = filepath_input
        with open(self.filepath, "r") as params:
            self.params_data = json.load(params)
        self.scan_time = datetime.today()

    def test_soup_outputs(self):
        homepage_url_retriever = HomepageURLRetriever(
            self.params_data["hp_url"], self.params_data["url"], 
            self.params_data["container"])
        url_list: list[str] = homepage_url_retriever.urls_to_list()

        soup_list = URLListToSoupList.url_list_to_soup_list(self.scan_time, url_list)

        for tuple in soup_list:
            print(f"Scan time: {tuple[0].strftime("%Y-%m-%dT%H:%M:%S")}, title: {tuple[1].title.string}")

if __name__ == '__main__':
    test = TestURLListToSoupList()
    test.test_soup_outputs()