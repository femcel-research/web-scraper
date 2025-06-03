from pathlib import Path
from utils.processing.meta_handling import MetaCollector
from htmldate import find_date
from bs4 import BeautifulSoup
import json
import requests
import datetime
import os
import re

class SiteMetaCollector:
    def __init__(self, url: str, soup: BeautifulSoup, folder_path: str):
        """Collects site-wide metadata from a website and stores it in a JSON file"""
        # Website info
        self.soup = soup
        self.url = url

        # File path
        self.folder_path = folder_path
        self.file_name = self.soup.title.string + "_meta.json"
        self.file_path = os.path.join(self.folder_path, self.file_name)
        
    def page_info_to_JSON(self):
        """Captures site URL, description, keywords"""
        # If meta keywords has content create a variable with that content, otherwise set to empty string
        meta_keywords = self.soup.find("meta", attrs={"name": "keywords"})
        if meta_keywords:
            keywords = meta_keywords["content"]
        else:
            keywords = ""

        # If meta description has content create a variable with that content, otherwise set to empty string
        meta_description = self.soup.find("meta", attrs={"name": "description"})
        if meta_description:
            description = meta_description["content"]
        else:
            description = ""

        info = {
            "URL": self.url,
            "site_title": self.soup.title.string,
            "description": description,
            "keywords": keywords,
        }
        return info
    
    def meta_dump(self):
        """Dumps website metadata into a JSON file"""
        metadata = {**self.page_info_to_JSON()}

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
