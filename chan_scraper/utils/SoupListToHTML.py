# Imports
import os

from bs4 import BeautifulSoup

class SoupListToHTML:
    """Saves a list of URL's HTML data into individual files."""
    @staticmethod
    def soup_list_to_html(
            soup_list: list[BeautifulSoup], scan_time: str, scrape_dir: str):
        """For each BeautifulSoup object, an HTML file is saved.
        
        Each HTML file is saved by thread ID number, to an internally
        specified file directory (based on arguments).

        Args:
            soup_list: List of BeautifulSoup objects.
            scan_time: Time of scan.
            scrape_dir: Directory for scrape data.
        """
        # Each batch of URLs/BeautifulSoup objects can have multiple instances
        # of the same thread. Each duplicate URL will lead to the same,
        # up-to-date instance of a thread. Therefore, if a thread has been
        # scraped once, it doesn't need to be scraped again.
        thread_set: set[str] = []  
        for soup in soup_list:
            thread_number = soup.find(class_="intro").get("id")
            if thread_number not in thread_set:
                thread_set.add(thread_number)
                html_file_name = f"thread_{thread_number}.html"
                # html_file_path = os.path.join(
                #     f"{data_dir}/{site_dir}/{thread_number}/{scan_time}",
                #     html_file_name)
                html_file_path = f"{scrape_dir}\
                    {thread_number}{os.sep}{scan_time}\
                    {os.sep}{html_file_name}"
                with open(html_file_path, "w") as file:
                    file.write(soup.prettify())
