# Imports
from datetime import datetime

from . import ScrapeData
from . import ThreadData

class ScrapeListToThreadList:
    """Returns a list of ThreadData objects given a valid ScrapeData list."""
    def __init__(
        self, scrapes: list[ScrapeData]):
        """Given a valid ScrapeData list, makes a list of ThreadData objects.

        If more than one ScrapeData with the same thread_number and datetime
        exist, only one will be added to a corresponding ThreadData
        object.

        The list of ThreadData objects can be retrieved via a getter.
        
        Args:
            scrapes: List of ScrapeData objects.    

        Attributes:
            self.thread_list: List of ThreadData objects.
        """
        self.thread_list: list[ThreadData] = []
        for scrape in scrapes:
            # Get thread number
            thread_number = scrape.get_thread_number()
            # Try to retrieve an existing ThreadData that corresponds to it
            thread: ThreadData = self.find_thread(thread_number)
            # If one doesn't exist, make a new one and add it to thread_list
            if thread is None:
                new_thread = ThreadData(thread_number)
                self.thread_list.append(new_thread)
                thread = new_thread
            # Check if an identical ScrapeData object exists in ThreadData
            scan_time: datetime = scrape.get_scan_time()
            if self.can_add_to_thread(thread, scan_time):
                # Add if it doesn't exist
                thread.add_scrape(scrape)                
        
    def find_thread(self, thread_number: str):
        """Returns a ThreadData with the same thread_number if it exists."""
        for thread in self.thread_list:
            if thread.get_thread_number() == thread_number:
                return thread
        return None
    
    def can_add_to_thread(self, thread: ThreadData, scan_time: datetime):
        """Returns False if a ScrapeData with the specified datetime exists.
        
        If a ScrapeData in the passed ThreadData object shares the same
        datetime (indicating a BeautifulSoup object with an identical
        state, as this check should only be called with a datetime
        retrieved from a ScrapeData object that shares
        the same thead_number as the ThreadData object), then returns
        False. Otherwise True.

        Args:
            thread: A ThreadData object with the same thread_number.
            date: A datetime object of a scrape with the same thread_number.
        """
        for scrape in thread.get_scrapes():
            if scrape.get_scan_time() == scan_time:  # The datetime
                return False
        return True

    def get_thread_list(self):
        return self.thread_list
