import glob
import json
import os
from pathlib import Path
from .StatCollector import StatCollector


class ThreadStatHandler(StatCollector):
    """Manages thread statistics.

        Args:
            thread_meta: Filepath of a thread's meta file.
        """

    def __init__(self, thread_meta: str, site_title: str):
        """Initializes with thread meta stats if it exists already; otherwise sets everything to 0"""
        super().__init__()
        self.site_title = site_title

        if os.path.exists(thread_meta):
            with open(thread_meta) as json_file:
                data = json.load(json_file)
                self.thread_id = data["thread_number"]
            json_file.close()
        else:
            parts = Path(thread_meta).parts  # split path by backslashes
            self.thread_id = parts[-2]

        self.thread_meta = thread_meta

        self.dist_post_ids = set()
        self.new_post_ids = set()
        self.new_lost_ids = set()

        self.all_post_ids = set()
        self.lost_post_ids = set()

        self.set_thread_values()  # Initializes values
        self.num_dist_posts = len(self.dist_post_ids)
        self.num_total_posts = len(self.all_post_ids)
        self.num_lost_posts = len(self.lost_post_ids)

    def get_thread_meta(self):
        """Returns a dictionary for a JSON file of dist_post_ids, lost_post_ids, num_dist_posts
        num_total_posts, num_lost_posts"""

        return {
            "dist_post_ids": self.dist_post_ids,
            "lost_post_ids": self.lost_post_ids,
            "num_dist_posts": self.num_dist_posts,
            "num_total_posts": self.num_total_posts,
            "num_lost_posts": self.num_lost_posts,
        }

    def get_scan_meta(self):
        """Returns a dictionary for a JSON file of all_post_ids, new_post_ids, new_lost_posts
        num_all_posts, num_new_posts, num_new_lost_posts"""
        all_ids = self.collect_post_ids(self.thread_meta)
        new_lost_ids = self.new_lost_ids
        new_ids = self.new_post_ids

        return {
            "all_post_ids": all_ids,
            "new_post_ids": new_ids,
            "new_lost_posts": new_ids,
            "num_all_posts": len(all_ids),
            "num_new_posts": len(new_ids),
            "num_new_lost_posts": len(new_lost_ids)
        }

    def set_thread_values(self) -> None:
        thread_path = os.path.join("./data", self.site_title, self.thread_id)
        master_path = os.path.join(
            "./data", self.site_title, self.thread_id, f"master_version{self.thread_id}.json")
        self.calculate_total_posts(self.thread_meta)  # total posts
        self.collect_all_post_ids(thread_path)  # distinct ids
        self.collect_lost_posts(
            self.distinct_post_ids, self.thread_meta)  # lost posts
        self.collect_new_posts(self.dist_post_ids, master_path)  # new posts
