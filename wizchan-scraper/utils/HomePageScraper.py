from htmldate import find_date
from bs4 import BeautifulSoup
import json
import requests
import datetime
import os
from utils import SiteMetaCollector

class HomePageScraper:
    """Makes a list of urls from homepage"""

    def __init__(self, url, site_title):
        self.page = requests.get(url, stream=True)  
        self.soup = BeautifulSoup(self.page.content, "html.parser")
        self.url_list = []
        self.site_title = site_title
        
        # JSON sitewide metadata file
        site_meta = SiteMetaCollector(self.page, self.soup, self.site_title, "./data/wizchan/")
        (site_meta.meta_dump())


    def urls_to_list(self):
        box_right = self.soup.find(class_="box right")
        lists_box_right = box_right.find_all("li")

        for list in lists_box_right:
            anchor_tag = list.find("a")
            if anchor_tag:
                url = anchor_tag.get("href")  # Get the value of "href" attribute; url info
                self.url_list.append("https://wizchan.org" + url)

        return(self.url_list)

