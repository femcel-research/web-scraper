# Imports
import json

from ..src import HomepageURLRetriever

# Run as module to make relative import work:
# python -m chan_scraper.tests.TestHomepageURLRetriever
# from web-scraper

class TestHomepageURLRetriever: 
    """Performs visual tests with prints on TestHomepageURLRetriever.
    
    Confirms the appropriate parameters are utilized and a list of
    URLs is retrieved.
    """   
    def __init__(self):
        filepath_input = input("Enter params filepath \n")
        # Using ./data/params/tests/test_params.json right now
        self.filepath = filepath_input
        with open(self.filepath, "r") as params:
            self.params_data = json.load(params)

    def test_param_outputs(self):
        """Prints parameters used in initialization."""
        print(f"Params are {self.params_data["hp_url"]},{self.params_data["domain"]}, {self.params_data["container"]}\n")

    def test_retriever_outputs(self):
        """Prints out a list of URLs that have been retrieved."""
        homepage_url_retriever = HomepageURLRetriever(
            self.params_data["hp_url"], self.params_data["domain"], 
            self.params_data["container"])
        url_list: list[str] = homepage_url_retriever.urls_to_list()

        print(url_list)

if __name__ == '__main__':
    test = TestHomepageURLRetriever()
    test.test_param_outputs()
    test.test_retriever_outputs()
    