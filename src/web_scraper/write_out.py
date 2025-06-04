# Imports
from bs4 import BeautifulSoup
from datetime import datetime

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