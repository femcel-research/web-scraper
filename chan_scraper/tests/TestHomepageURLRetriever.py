# Imports
import json
import unittest

from ..utils import HomepageURLRetriever

# Run as module to make relative import work:
# python -m chan_scraper.tests.TestHomepageURLRetriever

class TestHomepageURLRetriever(unittest.TestCase): 
    """Performs visual tests with prints on TestHomepageURLRetriever.
    
    Confirms the appropriate parameters are utilized and a list of
    URLs is retrieved.
    """   
    def test_param_outputs(self):
        hp_url: str
        domain: str
        container: str
        filepath = input("Enter params filepath \n")
        # Using ./data/params/tests/test_params.json right now

        with open(filepath, "r") as params:
            params_data = json.load(params)
            hp_url = params_data["hp_url"]
            domain = params_data["domain"]
            container = params_data["container"]

        print(f"Params are {hp_url}, {domain}, {container}\n")

    def test_retriever_outputs(self):
        hp_url: str
        domain: str
        container: str
        filepath = input("Enter params filepath \n")
        
        with open(filepath, "r") as params:
            params_data = json.load(params)
            hp_url = params_data["hp_url"]
            domain = params_data["domain"]
            container = params_data["container"]
            
        homepage_url_retriever = HomepageURLRetriever(
            hp_url, domain, 
            container)
        url_list: list[str] = homepage_url_retriever.urls_to_list()

        print(url_list)

if __name__ == '__main__':
    unittest.main()
    