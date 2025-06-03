import json
import os
from .ThreadScanStats import ThreadScanStats


class SiteStats:
    def __init__(self, site_meta_filepath: str, site_title: str = ""):
        """
        Initializes with site meta stats from a file if it exists,
        otherwise sets everything to default (0).
        """
        self.site_meta_filepath = site_meta_filepath
        self.site_title = site_title

        self.num_sitewide_threads = 0
        self.num_sitewide_total_posts = 0
        self.num_sitewide_dist_posts = 0

        if os.path.exists(self.site_meta_filepath):
            with open(self.site_meta_filepath, 'r') as json_file:
                data = json.load(json_file)
            self.num_sitewide_threads = data.get("num_sitewide_threads", 0)
            self.num_sitewide_total_posts = data.get(
                "num_sitewide_total_posts", 0)
            self.num_sitewide_dist_posts = data.get(
                "num_sitewide_dist_posts", 0)

    def update_from_thread_scan(self, thread_scan_stats: ThreadScanStats, is_new_thread: bool):
        """
        Updates site-wide statistics based on the results of a thread scan.
        """
        if is_new_thread:
            self.num_sitewide_threads += 1

        self.num_sitewide_total_posts += thread_scan_stats.num_all_posts
        self.num_sitewide_dist_posts += thread_scan_stats.num_new_posts

    def get_site_stats(self):
        """
        Returns a dictionary of site-wide statistics to be saved.
        """
        return {
            "num_sitewide_threads": self.num_sitewide_threads,
            "num_sitewide_total_posts": self.num_sitewide_total_posts,
            "num_sitewide_dist_posts": self.num_sitewide_dist_posts
        }

    def save_site_stats(self):
        """
        Saves the current site statistics to the specified file.
        """
        os.makedirs(os.path.dirname(self.site_meta_filepath), exist_ok=True)
        with open(self.site_meta_filepath, 'w') as json_file:
            json.dump(self.get_site_stats(), json_file, indent=4)
