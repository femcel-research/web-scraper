# Imports
import os

from utils import BuildNestDictionary
from utils import HomepageURLRetriever
from utils import InitializeNestDictionary
from utils import SoupListToContent
from utils import SoupListToHTML
from utils import SoupListToNestDictionary
from utils import URLListToSoupList

class FullScrape:
    """A "full scrape" collects HTML data, metadata, and statistics."""
    @staticmethod
    def full_scrape(params, homepage_url: str, scan_time: str):
        """Perform a "full scrape,": HTML data; post and site metadata; statistics.

        Args:
            filepath: Location of parameters JSON file.
            homepage_url: URL for homepage URL list retrieval.
            scan_time: Time of scan.

        Attributes:
            scrape_dir: Directory for current scrapes.
            TODO: Add rest?
        """
        scrape_dir: str = f"{params["data_dir"]}{os.sep}\
            {params["site_dir"]}{os.sep}"

        # Retrieve list of URLs
        # TODO: Make a parameter "domain", "container", etc. in params JSON
        homepage_url_retriever = HomepageURLRetriever(
            homepage_url, params["domain"], 
            params["container"])
        url_list: list[str] = homepage_url_retriever.urls_to_list()

        # Turn URL list to BeautifulSoup object list
        if url_list is not None:  # None if error
            soup_list = URLListToSoupList.url_list_to_soup_list(url_list)
        else:
            # TODO: Print error in log
            return None
        
        # Save HTML data for each BeautifulSoup object
        SoupListToHTML.soup_list_to_html(
            soup_list, scan_time, scrape_dir)
        
        # Save thread content for each BeautifulSoup object
        SoupListToContent.soup_list_to_content(
            soup_list, scan_time, scrape_dir, params["op_class"], 
            params["reply_class"], params["url"], 
            params["post_date_location"])
        
        # Create an empty nested dictionary for handling metadata and stats 
        # across prior and current scans
        nested_dictionary = BuildNestDictionary.build_nest_dictionary(
            soup_list)

        # Initialize the empty dictionary to be a skeleton with 
        # data from prior scans
        InitializeNestDictionary.initialize_nest_dictionary(nested_dictionary)

        # Make a copy of the skeleton dictionary and populate it 
        # with data from current BeautifulSoup object list
        # TODO: Finish working on: add scrape_dir, etc.
        filled_dictionary = (
            SoupListToNestDictionary.soup_list_to_nest_dictionary(
                soup_list, ))
        # SoupListToNestDictionary.soup_list_to_nest_dictionary(
        #     soup_list, nested_dictionary)

        # TODO: Used new populated dictionary

        # Collect site-wide metadata
        # TODO: Use nested dictionary; aggregate new post stats, etc. 
        # for this             
    