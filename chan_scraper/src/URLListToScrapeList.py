# Imports
import requests

from bs4 import BeautifulSoup
from datetime import datetime

from .ScrapeData import ScrapeData

class URLListToScrapeList:
    """A tool to return a list of ScrapeData objects, given a list of URLs."""
    @staticmethod
    def url_list_to_scrape_list(scan_time: datetime, url_list: list[str]):
        """Takes a URL list and returns a list of ScrapeData objects.

        Multiple ScrapeData objects corresponding to multiple
        links to the same thread (usually with different
        posts in the thread highlighted) will be returned in the list.
        All ScrapeData objects will be stored with the current
        scan time.

        Args:
            link_list: List of URLs.

        Returns:
            scrapes: List of ScrapeData objects.
        """
        scrapes: list[ScrapeData] = []
        for url in url_list:
            try:
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
                new_scrape = ScrapeData(scan_time, soup)
                scrapes.append(new_scrape)
            except requests.HTTPError as error:
                # TODO: Print error in log
                continue

        return scrapes