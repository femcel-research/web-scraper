# Imports
import os

from . import ScrapeData

class ScrapeListToHTML:
    """Saves a list of URL's HTML data into individual files."""
    @staticmethod
    def scrape_list_to_html(
            scrapes: list[ScrapeData], 
            site_dir: str):
        """For each ScrapeData object, an HTML file is saved.
        
        Each HTML file is saved by thread ID number, to an internally
        specified file directory (based on arguments).

        Args:
            scrapes: List of ScrapeData objects.
            scan_time: Time of scan.
            site_dir: Directory for scrape data.
        """
        # Each batch of URLs/BeautifulSoup objects can have multiple instances
        # of the same thread. Each duplicate URL will lead to the same,
        # up-to-date instance of a thread. Therefore, if a thread has been
        # scraped once, it doesn't need to be scraped again. Hence the set.
        thread_set: set[str] = set()  
        for scrape in scrapes:
            thread_number = scrape.get_thread_number()
            scan_time = scrape.get_scan_time().strftime("%Y-%m-%dT%H:%M:%S")
            if thread_number not in thread_set:
                thread_set.add(thread_number)

                html_file_name = f"thread_{thread_number}.html"

                html_file_path = f"{site_dir}{thread_number}{os.sep}{scan_time}{os.sep}{html_file_name}"

                os.makedirs(f"{site_dir}{thread_number}{os.sep}{scan_time}", exist_ok=True)

                with open(html_file_path, "w") as file:
                    file.write(tuple[1].prettify())