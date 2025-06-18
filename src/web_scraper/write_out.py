# Imports
import json
import os

from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path


def soup_to_html_file(source_soup: BeautifulSoup, html_file_path: str):
    """
    A soup object, made using a thread snapshot, is used to
    write out the snapshot's HTML after being prettified. The file
    is written out according to the directory in the passed
    `site_dir` parameter; the thread ID is extracted before writing and
    is used in conjunction with the scrape time to generate a path and
    file name.

    Args:
        source_soup (BeautifulSoup): Soup object of a thread snapshot's HTML.
        html_path (str): Directory for HTML files.
    """
    with open(html_file_path, "w", encoding="utf-8") as html:
        html.write(source_soup.prettify())

def snapshot_dict_to_json(
    data_dict: dict, date_scraped: str, thread_id: str, name: str, start_path: str
):
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

def format_date(date: datetime) -> str:
        """Formats datetime object to %Y-%m-%dT%H:%M:%S
        Args:
            date (datetime): Date to be formatted"""
        formatted_date: str = datetime.strftime(date, "%Y-%m-%dT%H:%M:%S")
        return formatted_date

def unix_to_datetime(unix_time: int) -> datetime:
        """Formats a UNIX timestamp into a datetime object
        Args:
            unix_time (int): UNIX timestamp"""
        datetime_obj = datetime.fromtimestamp(unix_time)
        return datetime_obj

def str_to_datetime(date_str: str) -> datetime:
        """Formats str to a datetime object.
        Args:
            date_str (str): Date to be turned into datetime"""
        datetime_obj: datetime = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        return datetime_obj
