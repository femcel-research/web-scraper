# Imports
import requests

from bs4 import BeautifulSoup

class URLListToSoupList:
    """A tool to return a list of Soup objects, given a list of URLs."""
    @staticmethod
    def url_list_to_soup_list(url_list: list[str]):
        """Takes a URL list and returns a list of BeautifulSoup objects.

        Args:
            link_list: List of URLs.

        Returns:
            soup_list: List of BeautifulSoup objects.
        """
        soup_list = []
        for url in url_list:
            try:
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
                soup_list.append(soup)
            except requests.HTTPError as error:
                # TODO: Print error in log
                continue

        return soup_list