# Imports
from utils import HomepageURLRetriever
from utils import URLListToSoupList

class MetaScrape:
    """A "meta scrape" collects metadata and statistics."""
    @staticmethod
    def meta_scrape(params, html_directory: str, scan_time: str):
        """ Perform a "meta scrape": post and site metadata.
        
        Args:
            filepath: Location of parameters JSON file.
            html_directory: Directory of HTML files to retrieve meta data from.
            scan_time: Time of scan.
        """
        # TODO: Fill out