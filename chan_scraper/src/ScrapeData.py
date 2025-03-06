# Imports
from bs4 import BeautifulSoup
from datetime import datetime

class ScrapeData:
    """Holds all of information associated with a given scrape of a thread."""
    def __init__(self, scan_time: datetime, soup: BeautifulSoup):
        """Contains all a BeautifulSoup object associated with a datetime.

        Holds a BeautifulSoup object, datetime (for the time of the scrape),
        thread number, and dictionary to hold individual scrape metadata.

        The thread_number is a string due to how BeautifulSoup retrieves it.

        Args:
            scan_time: Time of scrape.
            soup: BeautifulSoup created through scrape.
        
        Attributes:
            self.scan_time: Time of scrape datetime
            self.soup: BeautifulSoup object.
            self.thread_number: Thread ID number.
            self.scrape_meta: Dictionary containing scrape-specific data.
        """
        self.scan_time = scan_time
        self.soup = soup
        try:
            self.thread_number = self.soup.find(class_="intro").get("id")
            if self.thread_number is None:
                self.thread_number = self.soup.find(class_="intro").find("a")\
                    .get("id").replace("post_no_", "")
        except:
            pass  # TODO: Error
        self.scrape_meta: dict = {
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
                "num_tokens": 0,
                "num_dist_tokens": 0
                }
        
    def get_scan_time(self):
        return self.scan_time

    def get_soup(self):
        return self.soup

    def get_thread_number(self):
        return self.thread_number