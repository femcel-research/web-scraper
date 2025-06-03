import json
import os

from bs4 import BeautifulSoup
from .ThreadScanStats import ThreadScanStats
from .SiteStats import SiteStats


class MetaStatHandler:
    def __init__(self, thread_meta_path: str, soup: BeautifulSoup):
        """Initializes with thread meta stats if it exists already; otherwise sets everything to 0"""
        self.soup = soup
        self.thread_meta_path = thread_meta_path
        self.site_title = "crystal.cafe"  # TODO: abstract w params
        self.site_meta_file = os.path.join(
            "./data", self.site_title, f"{self.site_title}_meta.json")
        self.is_new_thread = not os.path.exists(thread_meta_path)
        self.thread_stats = ThreadScanStats(self.thread_meta_path)
        self.site_stats = SiteStats(self.site_meta_file, self.site_title)

    def collect_thread_stats(self):
        self.thread_stats.collect_scan_data(self.soup)
        self.thread_stats.save_thread_stats()

    def collect_site_stats(self):
        self.site_stats.update_from_thread_scan(
            self.thread_stats, self.is_new_thread)
        self.site_stats.save_site_stats()

    def get_scan_stats(self) -> dict:
        return self.thread_stats.get_scan_stats()

    def get_thread_stats(self) -> dict:
        return self.thread_stats.get_thread_stats()

    def get_site_stats(self) -> dict:
        return self.site_stats.get_site_stats()
