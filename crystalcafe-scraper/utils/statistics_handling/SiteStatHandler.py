import os
import json
from pathlib import Path
from .StatCollector import StatCollector


class SiteStatHandler(StatCollector):
    """Manages site statistics.

        Args:
            thread_meta: Filepath of a thread's meta file.
        """

    def __init__(self, thread_meta: str, site_title: str):
        """Initializes with thread meta stats if it exists already; otherwise sets everything to 0"""
        super().__init__()

        self.thread_meta = thread_meta
        self.site_title = site_title
        self.site_data = "./data"
        self.sitewide_lost_post_ids = set()
        self.sitewide_new_lost_ids = set()
        self.num_sitewide_total_threads = 0
        self.num_sitewide_total_posts = 0

        if os.path.exists(thread_meta):
            self.set_site_values()
        else:
            print("Given thread_meta does not exist in the directory.")

    def calculate_lost_posts(self, distinct_ids: set, master_version: str) -> None:
        """Calculates lost ids given a master version. Outputs a list whereas the initial index is a set contianing newly collected lost ids and the second is a set containing existing lost ids."""
        new_lost_ids = set()
        lost_ids = set()
        with open(master_version, "r") as json_file:
            master = json.load(json_file)
            master_post_ids = self.collect_all_post_ids(master)
            for post_id in distinct_ids:
                if post_id not in master_post_ids and post_id not in lost_ids:
                    new_lost_ids.add(post_id)
                    lost_ids.add(post_id)
        json_file.close()
        self.sitewide_lost_post_ids.update(lost_ids)
        self.sitewide_new_lost_ids.update(new_lost_ids)

    def set_site_values(self) -> None:
        """Sets values for sitewide posts, deleted"""
        directory = Path(self.site_data)
        total_threads = 0
        total_posts = 0
        if not directory.is_dir():
            print(f"Error: Directory not found: {self.site_data}")
            return

        for thread_folder in directory.iterdir():
            if not thread_folder.is_dir() or not list(thread_folder.glob("master_version*.json")):
                print(
                    f"Listed item in directory is not an eligible thread folder: {thread_folder.name}"
                )
                continue
            else:
                total_threads += 1
                master_version_files = list(
                    thread_folder.glob("master_version*.json"))
                if master_version_files:
                    master_version = master_version_files[0]
                    total_posts += self.calculate_total_posts(
                        str(master_version))

                    self.calculate_lost_posts(
                        thread_folder, master_version)
                else:
                    print(
                        f"Warning: No master_version file found in {thread_folder.name}")

        self.num_sitewide_total_threads = total_threads
        self.num_sitewide_total_posts = total_posts

    def get_site_meta(self):
        """Returns a dictionary for a JSON file of num_sitewide_threads, num_sitewide_total_posts, num_sitewide_dist_posts"""
        return {
            "num_sitewide_threads": self.num_sitewide_total_threads,
            "num_sitewide_total_posts": self.num_sitewide_total_posts,
            "num_sitewide_dist_posts": list(self.all_post_ids)
        }
