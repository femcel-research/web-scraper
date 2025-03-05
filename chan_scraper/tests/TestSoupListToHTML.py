# Imports
import datetime
import unittest

from ..utils import SoupListToHTML
from ..utils import URLListToSoupList

# Run as module to make relative import work:
# python -m chan_scraper.tests.TestSoupListToHTML

class TestSoupListToHTML(unittest.TestCase): 
    """Performs temp dir tests with temp HTML dir on SoupListToHTML."""   
    def test_html_outputs(self):
        scan_time = datetime.date.today().strftime("%Y-%m-%dT%H:%M:%S")
        scrape_dir = input("Provide the scrape directory\n")
        # Using ./chan_scraper/tests/HTML/ for now
        id_class = input("Provide an id_class for collecting thread IDs\n")
        # Likely "intro" or "post_anchor", depending on the site; check params

        url_list: list[str] = []
        url = input("Add one URL\n")  # Be sure to include "https://"
        url_list.append(url)
        url = input("Add another URL\n")
        url_list.append(url)
        url = input("Add one more URL\n")
        url_list.append(url)

        soup_list = URLListToSoupList.url_list_to_soup_list(url_list)

        SoupListToHTML.soup_list_to_html(
            soup_list, scan_time, 
            scrape_dir, id_class)

if __name__ == '__main__':
    unittest.main()