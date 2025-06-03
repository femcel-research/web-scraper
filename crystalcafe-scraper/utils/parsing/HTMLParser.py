import json
import logging
import os
from .SoupHandling import SoupHandling
from .meta_handling.MetaCollector import MetaCollector
from .html_handling.ContentCollector import ContentCollector
from .html_handling.MasterVersionGenerator import MasterVersionGenerator


class HTMLParser:

    """
    A tool for parsing a given URL and HTML file.
    """

    def __init__(self, url: str, html: str, snapshot_folder_path: str, thread_folder_path: str):
        """Parses HTML content
        
        Args:
            URL (str): A string containing a page's URL
            html (str): The raw HTML content of a page
            snapshot_folder_path (str): Path to snapshot folder
            thread_folder_path (str): Path to thread folder
        """

        self.url = url
        self.html = html
        self.html_soup = SoupHandling(html)
        self.snapshot_folder_path = snapshot_folder_path
        self.thread_folder_path = thread_folder_path

    def process_html(self, url, html):
        # Meta and Content Scans are done via the local HTML file
        id = self.html_soup.find(class_="intro").get("id")

   

        

        meta.get_thread_meta()
        logging.info(f"Saved/updated thread metadata for thread #{id}")

        meta.stat_handler.collect_site_stats()
        logging.info(f"Updated site-wide stats based on thread #{id}")

        # JSON master version file
        # TODO: probably a cleaner way to do this
        thread_meta_path = os.path.join(
            self.thread_folder_path.format(id), f"thread_meta_{id}.json"
        )
        with open(thread_meta_path, "r") as f:
            thread_meta = json.load(f)
        generator = MasterVersionGenerator(
            content.get_thread_contents(),
            thread_meta,
            id,
            self.thread_folder_path.format(id),
        )
        generator.write_master_thread()
        logging.info("Generated/updated master thread for thread #" + id)

def generate_meta(self, id):
         # JSON current scan metadata file
                # TODO: specify site name w params
        meta = MetaCollector(
            self.url,
            self.html_soup,
            self.snapshot_folder_path.format(id, self.scan_time),
            self.thread_folder_path.format(id)
        )
        meta.get_site_meta()
        logging.info(f"Updated current site metadata")

        meta.get_scan_meta()
        logging.info(f"Saved current scan metadata for thread #{id}")

def generate_thread_content(self, id):
     # JSON current scan thread content file
        content = ContentCollector(
            self.html_soup, self.snapshot_folder_path.format(id, self.scan_time)
        )
        content.write_thread()
        logging.info(f"Saved current thread content for thread #{id}")