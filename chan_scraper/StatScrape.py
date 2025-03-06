# Imports
from src import HomepageURLRetriever
from src import URLListToSoupList

class StatScrape:
    """A "stat scrape" collects statistics."""
    @staticmethod
    def stat_scrape(params, json_directory, scan_time: str):
        """ Perform a "stat scrape": content statistics.
        
        Args:
            filepath: Location of parameters JSON file.
            json_directory: Directory of JSON files to retrieve content from.
            scan_time: Time of scan.
        """
        # TODO: Fill out