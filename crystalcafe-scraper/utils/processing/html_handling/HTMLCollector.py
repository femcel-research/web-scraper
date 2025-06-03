from requests_html import HTMLSession
from bs4 import BeautifulSoup
import os


class HTMLCollector:
    """Allows a URL's HTML to be saved locally or returned as a string"""

    def __init__(self, soup: BeautifulSoup, folder_path: str):
        self.soup = soup
        self.folder_path = folder_path

        self.thread_id: str = self.soup.find(class_="intro").get("id")
        self.html_file_name: str = "thread_" + self.thread_id + ".html"
        self.html_file_path: str = os.path.join(self.folder_path, self.html_file_name)

    def saveHTML(self) -> None:
        """Saves URL's HTML locally"""
        with open(self.html_file_path, "w") as f:
            f.write(self.soup.prettify())

    def getHTML(self) -> str:
        """Returns URL's HTML as a string"""
        html_file_path: str = os.path.join(self.folder_path, self.html_file_name)

        # If an HTML file is not yet saved locally, save it then read from the file.
        if not os.path.exists(html_file_path):
            self.saveHTML()
        with open(html_file_path, "r") as f:
            html_content = f.read()
        return html_content
