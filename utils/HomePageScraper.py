from htmldate import find_date
from bs4 import BeautifulSoup
import json
import requests
import datetime
import os

class HomePageScraper:
    """Makes a list of urls from homepage"""

    def __init__(self, url):
        self.page = requests.get(url, stream=True)  
        self.soup = BeautifulSoup(self.page.content, "html.parser")

        self.url_list = []

    def urls_to_list(self):
        box_right = self.soup.find(class_="box right")
        lists_box_right = box_right.find_all("li")

        for list in lists_box_right:
            anchor_tag = list.find("a")
            if anchor_tag:
                url = anchor_tag.get("href")  # Get the value of "href" attribute; url info
                self.url_list.append("https://crystal.cafe" + url)

        print(self.url_list)
        print()

        return(self.url_list)

