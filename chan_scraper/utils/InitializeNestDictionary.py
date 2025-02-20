# Imports
import json
import os

from bs4 import BeautifulSoup
from pathlib import Path

class InitializeNestDictionary:
    """Initializes dictionary with thread_meta files from prior scrapes."""
    @staticmethod
    def initialize_nest_dictionary(
        soup_list: list[BeautifulSoup], nested_dictionary, scrape_dir: str):
        """The nested dictionary is initialized with prior thread_meta files.

        If a thread_meta file exists for a thread from a previous scrape, then
        the values from that thread_meta file will be used to initialize
        the thread_meta sub-dictionary for each BeautifulSoup object's URL.

        Args:
            soup_list: List of BeautifulSoup objects.
            nested_dictionary: Empty nested dictionary with one key per URL.
            scrape_dir: Directory for scrape data.
        """
        for soup in soup_list:
            thread_number = soup.find(class_="intro").get("id")
            thread_meta_path = Path(f"{scrape_dir}\
                {thread_number}{os.sep}thread_meta_{thread_number}")
            if thread_meta_path.exists():
                with open(thread_meta_path, "r") as thread_meta:
                    meta = json.load(thread_meta)
                    for k in meta:  # For key in meta
                        if k in nested_dictionary[soup.url]["thread_meta"]:
                            nested_dictionary[soup.url]["thread_meta"][k] = (
                                meta[k])
        


