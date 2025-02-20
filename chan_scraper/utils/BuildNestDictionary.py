# Imports
from bs4 import BeautifulSoup

class BuildNestDictionary:
    """Creates a nested dictionary with keys for each BeautifulSoup object."""
    @staticmethod
    def build_nest_dictionary(soup_list: list[BeautifulSoup]):
        """For each BeautifulSoup object, an assoc. key/value pair is made.

        An empty nested dictionary is constructed, with the outermost keys
        corresponding to the thread_numbers of each BeautifulSoup object. 
        Inner keys correspond to thread_meta files from prior scrapes, and 
        the current scrape. If a thread_number already has an entry in the
        dictionary, then another dictionary is not made because duplicate
        URLs that point to the same thread contain the same content if
        accessed at the same time.

        Args:
            soup_list: List of BeautifulSoup objects.
        """
        nested_dictionary = {}

        for soup in soup_list:
            thread_number = soup.find(class_="intro").get("id")
            if thread_number not in soup_dictionary:
                soup_dictionary = {
                    "thread_meta": {
                        "URL": "",
                        "board": "",
                        "thread_title": "",
                        "thread_number": "",
                        "date_published": "",
                        "date_updated": "",
                        "date_scraped": "",
                        "dist_posts": [],
                        "lost_posts": [],
                        "num_dist_posts": 0,
                        "num_total_posts": 0,
                        "num_lost_posts": 0,
                        "num_tokens": 0,  # TODO: New; implement
                        "num_dist_tokens": 0  # TODO: New; implement
                    },
                    "current_scrape": {
                        "URL": "",
                        "board": "",
                        "thread_title": "",
                        "thread_number": "",
                        "date_published": "",
                        "date_updated": "",
                        "date_scraped": "",
                        "all_posts": [],
                        "new_posts": [],
                        "new_lost_posts": [],
                        "num_all_posts": 0,
                        "num_new_posts": 0,
                        "num_new_lost_posts": 0,
                        "num_tokens": 0,  # TODO: New; implement
                        "num_dist_tokens": 0  # TODO: New; implement  
                    }
                }
                nested_dictionary[thread_number] = soup_dictionary
        return nested_dictionary
