import json
import os

from bs4 import BeautifulSoup


class ThreadScanStats:
    def __init__(self, thread_meta_filepath: str):
        """
        Initializes with thread meta stats from a file if it exists,
        otherwise sets everything to default (0 or empty lists).
        """
        self.thread_meta_filepath = thread_meta_filepath

        # Thread-specific stats
        self.dist_post_ids = []  # All distinctive post_ids across all scans for this thread
        self.lost_post_ids = []  # Post IDs that were once seen but are no longer present
        self.num_dist_posts = 0  # Count of distinctive posts
        self.num_total_posts = 0  # Total posts seen across all scans
        self.num_lost_posts = 0  # Count of lost posts

        if os.path.exists(self.thread_meta_filepath):
            with open(self.thread_meta_filepath, 'r') as json_file:
                data = json.load(json_file)
            self.dist_post_ids = data.get("dist_post_ids", [])
            self.lost_post_ids = data.get("lost_post_ids", [])
            self.num_dist_posts = data.get("num_dist_posts", 0)
            self.num_total_posts = data.get("num_total_posts", 0)
            self.num_lost_posts = data.get("num_lost_posts", 0)

        # Scan-specific temp stats (calculated each scan)
        self.all_post_ids = []       # All post_ids found in the current scan
        self.new_post_ids = []       # Post IDs that are new in this scan
        self.new_lost_posts = []     # Post IDs newly identified as lost in this scan
        self.num_all_posts = 0       # Number of posts in the current scan
        self.num_new_posts = 0       # Number of new posts in this scan
        self.num_new_lost_posts = 0  # Number of newly lost posts in this scan

    def collect_scan_data(self, soup: BeautifulSoup):
        """
        Collects post IDs from the current scan and updates thread-specific
        and scan-specific statistics.
        """
        self.all_post_ids = []
        original_post = soup.find(class_="post op")
        if original_post:
            self.all_post_ids.append(
                original_post.find(class_="intro").get("id"))

        for reply in soup.find_all(class_="post reply"):
            self.all_post_ids.append(reply.find(class_="intro").get("id"))

        self.num_all_posts = len(self.all_post_ids)
        self.num_total_posts += self.num_all_posts

        # Identify new posts and update distinctive posts
        self.new_post_ids = []
        for post_id in self.all_post_ids:
            if post_id not in self.dist_post_ids:
                self.new_post_ids.append(post_id)
                self.dist_post_ids.append(post_id)
        self.num_new_posts = len(self.new_post_ids)
        self.num_dist_posts = len(self.dist_post_ids)

        # Identify new lost posts
        self.new_lost_posts = []
        self.num_new_lost_posts = 0
        for post_id in list(self.dist_post_ids):
            if post_id not in self.all_post_ids and post_id not in self.lost_post_ids:
                self.new_lost_posts.append(post_id)
                self.lost_post_ids.append(post_id)
                self.num_new_lost_posts += 1
        self.num_lost_posts = len(self.lost_post_ids)

    def get_thread_stats(self):
        """
        Returns a dictionary of persistent thread statistics to be saved.
        """
        return {
            "dist_post_ids": self.dist_post_ids,
            "lost_post_ids": self.lost_post_ids,
            "num_dist_posts": self.num_dist_posts,
            "num_total_posts": self.num_total_posts,
            "num_lost_posts": self.num_lost_posts
        }

    def get_scan_stats(self):
        """
        Returns a dictionary of statistics from the current scan.
        """
        return {
            "all_post_ids": self.all_post_ids,
            "new_post_ids": self.new_post_ids,
            "new_lost_posts": self.new_lost_posts,
            "num_all_posts": self.num_all_posts,
            "num_new_posts": self.num_new_posts,
            "num_new_lost_posts": self.num_new_lost_posts
        }

    def save_thread_stats(self):
        """
        Saves the current thread statistics to the specified file.
        """
        os.makedirs(os.path.dirname(self.thread_meta_filepath), exist_ok=True)
        with open(self.thread_meta_filepath, 'w') as json_file:
            json.dump(self.get_thread_stats(), json_file, indent=4)
