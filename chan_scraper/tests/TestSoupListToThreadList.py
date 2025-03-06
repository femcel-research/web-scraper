# Imports
import json

from datetime import datetime

from ..src import HomepageURLRetriever
from ..src import SoupListToThreadList
from ..src import URLListToSoupList

# Run as module to make relative import work:
# python -m chan_scraper.tests.TestSoupListToThreadList

class TestSoupListToThreadList:
    """Performs a visual test with prints on SoupListToThreadList
    
    Uses the __str__ override for ThreadData objects to confirm
    the number of unique threads among soup_list and the number of
    unique scan times. The outputted "number of tuples" for each thread
    should be 1, as every BeautifulSoup object was scraped simultaneously.
    """
    def __init__(self):
        filepath_input = input("Enter params filepath \n")
        # Using ./data/params/tests/test_params.json right now
        filepath = filepath_input
        with open(filepath, "r") as params:
            self.params_data = json.load(params)
        self.scan_time = datetime.today()
        homepage_url_retriever = HomepageURLRetriever(
            self.params_data["hp_url"], self.params_data["url"], 
            self.params_data["container"])
        url_list: list[str] = homepage_url_retriever.urls_to_list()

        self.soup_list = URLListToSoupList.url_list_to_soup_list(self.scan_time, url_list)

    def test_thread_print(self):
        soup_list_to_thread_list_object = SoupListToThreadList(self.soup_list)
        thread_list = soup_list_to_thread_list_object.get_thread_list()
        for thread in thread_list:
            print(thread)

if __name__ == '__main__':
    test = TestSoupListToThreadList()
    test.test_thread_print()