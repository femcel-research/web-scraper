# Imports
import datetime
import unittest

from ..utils import SoupListToContent
from ..utils import URLListToSoupList

# Run as module to make relative import work:
# python -m chan_scraper.tests.TestSoupListToContent

class TestSoupListToContent(unittest.TestCase): 
    """Performs temp dir tests with temp Content dir on SoupListToContent."""   
    def test_content_outputs(self):
        scan_time = datetime.date.today().strftime("%Y-%m-%dT%H:%M:%S")
        scrape_dir = input("Provide the scrape directory\n")
        # Using ./chan_scraper/tests/Content/ for now
        op_class = input("Provide an op_class for collecting original posts\n")
        # Likely "post op", depending on the site; check params
        reply_class = input("Provide a reply_class for collecting replies\n")
        # Likely "post reply"
        url = input("Provide a URL to precede image links\n")
        # Likely identical to hp_url
        post_date_location = input("Provide a post_date_location\n")
        # Likely "post_no date-link" or "delete_"

        url_list: list[str] = []
        url = input("Add one URL\n")  # Be sure to include "https://"
        url_list.append(url)
        url = input("Add another URL\n")
        url_list.append(url)
        url = input("Add one more URL\n")
        url_list.append(url)

        soup_list = URLListToSoupList.url_list_to_soup_list(url_list)

        to_content_instance = SoupListToContent()
        to_content_instance.soup_list_to_content(
            soup_list, scan_time, 
            scrape_dir, op_class,
            reply_class, url,
            post_date_location)

if __name__ == '__main__':
    unittest.main()