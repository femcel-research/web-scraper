from string import Template
from htmldate import find_date
from bs4 import BeautifulSoup
import json
import requests
import datetime
import os
import re
from .MetaStatHandler import MetaStatHandler



# add automatic html, meta, thread folders
class MetaCollector:
    """Collects metadata from a website and stores it in a JSON file"""
    THREAD_META_PATH = Template("./data/crystalcafe/$t/thread_meta_$t.json")  # $t for thread id

    def __init__(self, url, thread_html, soup, folder_path, is_thread_meta):
        # Website info
        self.html_content = thread_html
        self.soup = soup
        self.url = url
        self.id = soup.find('div', class_="thread").get('id').strip('thread_') 

        # File path
        if is_thread_meta:
            file_name = "thread_meta_{}.json".format(self.id)
        else:
            file_name = "meta_{}.json".format(self.id)
        self.file_path = os.path.join(folder_path, file_name)

        json_path = self.THREAD_META_PATH.substitute(t = id)
        self.stat_handler = MetaStatHandler(json_path)

    def date_to_JSON(self):
        """Captures date published, date updated, and date scraped from a specified website"""

        # Uses htmldate lib to find original and update dates
        publish_Date = find_date(
            self.html_content,
            extensive_search=True,
            original_date=True,
            outputformat="%Y-%m-%dT%H:%M:%S",
        )
        update_Date = find_date(
            self.html_content,
            extensive_search=True,
            original_date=False,
            outputformat="%Y-%m-%dT%H:%M:%S",
        )

        # Assumption is that each time this func is run during scrape, it will capture the time of scrape
        scrape_date = datetime.datetime.now()
        formatted_date = scrape_date.strftime("%Y-%m-%dT%H:%M:%S")

        dates = {
            "date_published": publish_Date,
            "date_updated": update_Date,
            "date_scraped": formatted_date,
        }

        return dates

    def page_info_to_JSON(self):
        """Captures page URL, title, description, keywords, site info"""

        # page = requests.get(self.URL, stream=True)
        page = self.html_content
        # soup = BeautifulSoup(page.content, "html.parser")
        
        # Splits board and thread title
        page_title = self.soup.title.string
        board_and_title = re.split('[-]',page_title)
        for x in range(len(board_and_title)):
            board_and_title[x] = board_and_title[x].strip()
        board = board_and_title[0]
        title = board_and_title[1]

        info = {
            "URL": self.url,
            "board": board,
            "thread_title": title,
            "thread_number": self.id,
        }
        return info

    def meta_dump(self, is_thread_meta):
        """Dumps website metadata into a JSON file; if is_thread_meta, dumps thread values, else updates site_meta and dumps scan values"""

        if is_thread_meta:
            self.stat_handler.set_scan_and_thread_values(self.soup)
            self.stat_handler.update_site_meta(True)
            metadata = {**self.page_info_to_JSON(), **self.date_to_JSON(), **self.stat_handler.get_thread_meta()}   
        else:
            self.stat_handler.set_scan_and_thread_values(self.soup)
            self.stat_handler.update_site_meta(False)
            metadata = {**self.page_info_to_JSON(), **self.date_to_JSON(), **self.stat_handler.get_scan_meta()}

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
