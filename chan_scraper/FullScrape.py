# Imports
import os

# from bs4 import BeautifulSoup
from datetime import datetime

# from src import HomepageURLRetriever
# from src import SoupListToContent
# from src import SoupListToHTML
# from src import SoupListToMeta
# from src import URLListToSoupList
# TODO: Fix with new class structure!
class FullScrape:
    """A "full scrape" collects HTML data, metadata/stats, and site-wide.
    
    Site-wide data is incremented.
    """
    @staticmethod
    def full_scrape(params, scan_time: datetime):
        """Perform a "full scrape,": HTML data; post and site metadata; stats.

        Args:
            filepath: Location of parameters JSON file.
            homepage_url: URL for homepage URL list retrieval.
            scan_time: Time of scan.

        Attributes:
            homepage_url_retriever: HomepageURLRetriever object.
            url_list: List of URLs.
            soup_list: List of BeautifulSoup objects.
        """
        # scrape_dir: str = f"{params["data_dir"]}{os.sep}{params["site_dir"]}{os.sep}"

        # Retrieve list of URLs
        # homepage_url_retriever_object = HomepageURLRetriever(
        #     params["hp_url"], params["domain"], 
        #     params["container"])
        # url_list: list[str] = homepage_url_retriever_object.urls_to_list()

        # # Turn URL list to BeautifulSoup tuples list
        # if url_list is not None:  # None if error
        #     soup_list: list[tuple[datetime, BeautifulSoup]] = URLListToSoupList.\
        #         url_list_to_soup_list(scan_time, url_list)
        # else:
        #     # TODO: Print error in log
        #     return None  # TODO: Abort
        
        # # Save HTML data for each BeautifulSoup object
        # SoupListToHTML.soup_list_to_html(
        #     soup_list, scan_time, 
        #     params["site_dir"], params["id_class"])
        
        # # Turn BeautifulSoup tuples list to list of ThreadData objects
        # # TODO: Implement
        
        # # Save thread content for each BeautifulSoup object        
        # soup_list_to_content_object = SoupListToContent()
        # soup_list_to_content_object.soup_list_to_content(
        #     soup_list, scan_time, 
        #     params["site_dir"], params["op_class"], 
        #     params["reply_class"], params["url"], 
        #     params["post_date_location"])
        
        # # Save thread and current scrape metadata for each BeautifulSoup obj
        # soup_list_to_meta_object = SoupListToMeta()
        # soup_list_to_meta_object.soup_list_to_meta(...)

        # # Collect/update site-wide/aggregate metadata
        # aggregate_dictionary = soup_list_to_meta_object.\
        #     get_aggregate_dictionary()
        # TODO: Make a util to update or overwrite aggregate dict,
        # depending on if you're doing a normal scrape and want to add
        # to current statistics, or if you're doing a re-scrape of all past
        # data and want to "rebase"
                    
    