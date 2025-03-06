# Imports
import datetime
import json

from ..src import HomepageURLRetriever
from ..src import SoupListToThreadList
from ..src import ThreadListToContent
from ..src import URLListToSoupList

# Run as module to make relative import work:
# python -m chan_scraper.tests.TestThreadListToContent

class TestThreadListToContent(): 
    """Performs test with test directory on ThreadListToContent."""  
    def __init__(self):
        filepath_input = input("Enter params filepath \n")
        # Using ./data/params/tests/test_params.json right now
        self.filepath = filepath_input
        with open(self.filepath, "r") as params:
            self.params_data = json.load(params)
        scan_time = datetime.datetime.today()
        homepage_url_retriever = HomepageURLRetriever(
            self.params_data["hp_url"], self.params_data["url"], 
            self.params_data["container"])
        url_list: list[str] = homepage_url_retriever.urls_to_list()
        soup_list = URLListToSoupList.url_list_to_soup_list(scan_time, url_list)
        soup_list_to_thread_list_object = SoupListToThreadList(soup_list)
        self.thread_list = soup_list_to_thread_list_object.get_thread_list()
         
    def test_content_scrape(self):
        """Given valid parameters, populates a directory with content."""
        thread_list_to_content_object = ThreadListToContent()
        thread_list_to_content_object.thread_list_to_content(
            self.thread_list, self.params_data["site_dir"], self.params_data["op_class"],
            self.params_data["reply_class"], self.params_data["url"],
            self.params_data["post_date_location"]
        )

if __name__ == '__main__':
    test = TestThreadListToContent()
    test.test_content_scrape()