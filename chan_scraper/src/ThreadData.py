# Imports
from .ScrapeData import ScrapeData

class ThreadData:
    """Holds all of information associated with a given thread."""
    def __init__(self, thread_number: str):
        """Contains all ScrapeData objects associated with a thread ID.

        All ScrapeData objects associated with a given thread ID will
        be in a ThreadData object, sharing said ID. Metadata on the
        thread as a whole is also tracked in the relevant ThreadData object,
        and is set/reset when the appropriate method is called (with the
        appropriate data).

        This class is designed to hold a list of ScrapeData objects
        that correlate to an individual thread, and a
        dictionary for metadata for an individual thread.

        The thread_number is a string due to how BeautifulSoup retrieves it.

        Args:
            thread_number: Thread ID number.
        
        Attributes:
            self.thread_number: Thread ID number.
            self.scrapes: List of ScrapeData objects.
            self.thread_meta: Dictionary containing thread-wide data.
        """
        self.thread_number: str = thread_number
        self.scrapes: list[ScrapeData] = []
        self.thread_meta: dict = {
                "URL": "",
                "board": "",
                "thread_title": "",
                "thread_number": self.thread_number,
                "date_published": "",
                "date_updated": "",
                "date_scraped": "",
                "dist_posts": [],
                "lost_posts": [],
                "num_dist_posts": 0,
                "num_total_posts": 0,
                "num_lost_posts": 0,
                "num_tokens": 0,
                "num_dist_tokens": 0
                }

    def add_scrape(self, scrape: ScrapeData):
        self.scrapes.append(scrape)
        # Sort the list in ascending order based on datetime
        self.scrapes.sort(key=lambda x:x.get_scan_time()) 

    def get_scrapes(self):
        """Returns internal list of ScrapeData objects."""
        return self.scrapes

    def get_thread_number(self):
        return self.thread_number
    
    def get_thread_meta(self):
        """Used in ThreadListToMeta to initialize its dictionary/write out.
        
        Returns dictionary of thread_wide metadata.
        """
        return self.thread_meta
    
    def set_thread_meta(self, new_data: dict):
        """Uses new_data to set values of thread_meta dictionary.
        
        The new_data should be structured with the same keys as thread_meta.

        Used in ThreadListToMeta to set new values after a BeautifulSoup
        object has had metadata scraped from it. 

        DOES NOT += VALUES; OVERWRITES ACCORDING TO new_data

        Args:
            new_data: Dictionary with shared structure and new values.
        """
        self.thread_meta["URL"] = new_data["URL"]
        self.thread_meta["board"] = new_data["board"]
        self.thread_meta["thread_title"] = new_data["thread_title"]
        # self.thread_meta["thread_number"] = new_data["thread_number"]
        #Most recent scrape data ↓
        self.thread_meta["date_published"] = new_data["date_published"]
        self.thread_meta["date_scraped"] = new_data["date_scraped"]
        for post in new_data["dist_posts"]:
            if post not in self.thread_meta["dist_posts"]:
                self.thread_meta["dist_posts"].append(post)
        for post in new_data["lost_posts"]:
            if post not in self.thread_meta["lost_posts"]:
                self.thread_meta["lost_posts"].append(post)
        self.thread_meta["num_dist_posts"] = new_data["num_dist_posts"]
        self.thread_meta["num_total_posts"] = new_data["num_total_posts"]
        self.thread_meta["num_lost_posts"] = new_data["num_lost_posts"]
        self.thread_meta["num_tokens"] = new_data["num_tokens"]
        self.thread_meta["num_dist_tokens"] = new_data["num_dist_tokens"]

    def __str__(self):
        return f"ID: {self.thread_number}, number of scrapes: {len(self.scrapes)}"

        