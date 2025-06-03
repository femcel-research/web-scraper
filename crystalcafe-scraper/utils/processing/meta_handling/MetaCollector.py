from string import Template

from bs4 import BeautifulSoup
import json
import requests

import os
import re
from .DateFinder import DateFinder
from .MetaStatHandler import MetaStatHandler


# add automatic html, meta, thread folders
class MetaCollector:
    """Collects metadata from a website and stores it in a JSON file"""

    THREAD_META_PATH = Template(
        "./data/crystal.cafe/$t/thread_meta_$t.json"
    )  # $t for thread id

    def __init__(self, url, soup, scan_folder_path, thread_folder_path):
        # Website info
        self.soup = soup
        self.url = url
        self.file_path: str
        self.scan_folder_path = scan_folder_path
        self.thread_folder_path = thread_folder_path
        self.id = soup.find(class_="intro").get("id")

        json_path = self.THREAD_META_PATH.substitute(t=id)
        self.stat_handler = MetaStatHandler(json_path)
        self.stat_handler.set_scan_and_thread_values(self.soup)

    def get_dates(self):
        html:str = str(self.soup)
        datefinder = DateFinder(html)
        return datefinder.date_to_JSON()

    def page_info_to_JSON(self):
        """Captures page URL, title, description, keywords, site info"""

        # Splits board and thread title
        page_title = self.soup.title.string
        board_and_title = re.split("[-]", page_title)
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

    def get_scan_meta(self) -> None:
        file_name = f"meta_{self.id}.json"
        self.file_path = os.path.join(self.scan_folder_path, file_name)
        self.stat_handler.update_site_meta(False)
        dates: dict = self.get_dates()
        scan_meta_stats: dict = self.stat_handler.get_scan_meta()
        metadata = {**self.page_info_to_JSON(), **dates, **scan_meta_stats}
        self.meta_dump(metadata)

    def get_thread_meta(self) -> None:
        file_name = f"thread_meta_{self.id}.json"
        self.file_path = os.path.join(self.thread_folder_path, file_name)
        self.stat_handler.update_site_meta(True)
        dates: dict = self.get_dates()
        thread_meta_stats: dict = self.stat_handler.get_thread_meta()
        metadata = {**self.page_info_to_JSON(), **dates, **thread_meta_stats}
        self.meta_dump(metadata)

    def meta_dump(self, metadata):
        """Dumps website metadata into a JSON file; if is_thread_meta, dumps thread values, else updates site_meta and dumps scan values"""

        # if is_thread_meta:
        #     self.stat_handler.set_scan_and_thread_values(self.soup)
        #     self.stat_handler.update_site_meta(True)
        #     metadata = {**self.page_info_to_JSON(), **self.date_to_JSON(), **self.stat_handler.get_thread_meta()}
        # else:
        #     self.stat_handler.set_scan_and_thread_values(self.soup)
        #     self.stat_handler.update_site_meta(False)
        #     metadata = {**self.page_info_to_JSON(), **self.date_to_JSON(), **self.stat_handler.get_scan_meta()}

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
