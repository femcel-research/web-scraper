# Imports
import json
import os

from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

def soup_to_html_file(
        scrape_time: datetime, source_soup: BeautifulSoup, site_dir: str):
    """TODO: Writes a soup object to an HTML file.

    A soup object, made using a thread snapshot, is used to
    write out the snapshot's HTML after being prettified. The file
    is written out according to the directory in the passed
    `site_dir` parameter; the thread ID is extracted before writing and
    is used in conjunction with the scrape time to generate a path and
    file name.
    
    Args:
        scrape_time (datetime): Time of scrape.
        source_soup (BeautifulSoup): Soup object of a thread snapshot's HTML.
        site_dir (str): Directory for HTML files.
    """
    pass

def snapshot_dict_to_json(
        data_dict: dict, date_scraped: str, thread_id: str, 
        name: str, start_path: str):
    """Writes out dictionary of data for a thread snapshot to a JSON file.

    Files will be written to a JSON file according to the arguments passed:
    `f"{start_path}/{thread_id}/{date_scraped}/{name}_{thread_id}.json"`
    
    Args:
        data_dict (dict): Data to be written out.
        date_scraped (str): Date scraped.
        thread_id (str): Thread number.
        name (str): The name of the file (content, etc.)
        start_path (str): The directory for the data.
    """
    # TODO: Improve this method by adding tests and exception handling
    thread_data_path: str = f"{start_path}/{thread_id}/{date_scraped}/"
    os.makedirs(thread_data_path, exist_ok=True)
    individual_file_path: str = f"{thread_data_path}{name}_{thread_id}.json"
    if os.path.exists(thread_data_path):
        with open(individual_file_path, "w") as json_file:
            json.dump(data_dict, json_file, indent=4)