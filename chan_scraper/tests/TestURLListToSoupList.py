# Imports
import unittest

from ..utils import URLListToSoupList

# Run as module to make relative import work:
# python -m chan_scraper.tests.TestURLListToSoupList

class TestURLListToSoupList(unittest.TestCase): 
    """Performs visual tests with prints on URLListToSoupList.

    Uses unformatted BeautifulSoup object output for confirmation.
    """   
    def test_soup_outputs(self):
        url_list: list[str] = []
        url = input("Add one URL\n")  # Be sure to include "https://"
        url_list.append(url)
        url = input("Add another URL\n")
        url_list.append(url)
        url = input("Add one more URL\n")
        url_list.append(url)

        soup_list = URLListToSoupList.url_list_to_soup_list(url_list)

        print(soup_list)

if __name__ == '__main__':
    unittest.main()