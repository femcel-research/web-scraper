import json
import os
from pathlib import Path


class MetaStatHandler:
    def __init__(self, thread_meta):
        """Initializes with thread meta stats if it exists already; otherwise sets everything to 0"""
        if os.path.exists(thread_meta):
            with open(thread_meta) as json_file:
                self.data = json.load(json_file)

            # []; all distinctive post_ids across all scans
            self.dist_post_ids: set = set(self.data["dist_post_ids"])
            # []; everytime a post is in dist_post_ids but not all_post_ids && not in lost_post_ids already, add here
            self.lost_post_ids: set = set(self.data["lost_post_ids"])
            # += w/ num_new_posts
            self.num_dist_posts: int = self.data["num_dist_posts"]
            # Posts across all scans; += w/ num_all_posts
            self.num_total_posts: int = self.data["num_total_posts"]
            # Posts that formerly appeared, but did not in current scan
            self.num_lost_posts: int = self.data["num_lost_posts"]
        else:
            self.dist_post_ids: set = set()
            self.lost_post_ids: set = set()
            self.num_dist_posts: int = 0
            self.num_total_posts: int = 0
            self.num_lost_posts: int = 0

    def set_scan_and_thread_values(self, soup):
        """Sets the values for the current scan of the website and changes thread meta file values from initialized values
        accordingly"""
        # Get a masterlist of all posts
        self.all_post_ids: set = set()
        original_post = soup.find(class_="post op")
        self.all_post_ids.add(original_post.find(class_="intro").get("id"))

        for reply in soup.find_all(class_="post reply"):
            self.all_post_ids.add(reply.find(class_="intro").get("id"))

        # Get the title of the website for any use in update_site_meta()
        meta_keywords = soup.find("meta", attrs={"name": "keywords"})
        if meta_keywords:
            keywords: set = set(meta_keywords["content"])
        else:
            keywords = set()

        self.site_title = "crystal.cafe"
        self.site_data_path = os.path.join("./data", self.site_title)
        self.new_post_ids: set = set()
        self.new_lost_posts: set = set()
        self.num_new_lost_posts: int = 0
        self.num_sitewide_dist_posts: int = 0

        self.collect_new_and_dist()
        self.collect_lost()
        self.gather_totals()

    # Helper functions for setting scan and thread values:
    def collect_new_and_dist(self) -> None:
        """Make a list of all post_ids that aren't already in dist_post_ids in thread meta file"""
        for post_id in self.all_post_ids:
            if post_id not in self.dist_post_ids:
                self.new_post_ids.add(post_id)
                self.dist_post_ids.add(post_id)

    def collect_lost(self) -> None:
        """Make a list/tally the post_ids that were once added to dist_post_ids, but aren't in the current scan"""
        for post_id in self.dist_post_ids:
            if post_id not in self.all_post_ids and post_id not in self.lost_post_ids:
                self.new_lost_posts.add(post_id)
                self.lost_post_ids.add(post_id)
                self.num_new_lost_posts = len(self.new_lost_posts)

    def gather_totals(self) -> None:
        """Calculates number of all posts, new posts, distinct posts, total posts, and lost posts"""
        self.num_all_posts = len(self.all_post_ids)
        self.num_new_posts = len(self.new_post_ids)
        self.num_dist_posts = len(self.dist_post_ids)
        self.num_total_posts = self.num_dist_posts
        self.num_lost_posts += self.num_new_lost_posts

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
        """Sets values for the following sitewide statistics: num_sitewide_threads, num_sitewide_total_posts, and num_sitewide_dist_posts."""
        directory = Path(self.site_data_path)
        total_threads = 0
        total_posts = 0
        dist_posts = 0
        if not directory.is_dir():
            print(f"Error: Directory not found: {self.site_data_path}")
            return

        for thread_folder in directory.iterdir():
            if not thread_folder.is_dir() or not list(thread_folder.glob("master_version*.json")):
                # TODO: log this information at a later date!
                # print(
                #     f"Listed item in directory is not an eligible thread folder: {thread_folder.name}"
                # )
                continue
            else:
                total_threads += 1
                master_version_files = list(
                    thread_folder.glob("master_version*.json"))
                if master_version_files:
                    master_version = master_version_files[0]
                    total_posts += self.calculate_total_posts(
                        str(master_version))
                    dist_posts += self.num_dist_posts
                else:
                    print(
                        f"Warning: No master_version file found in {thread_folder.name}")

        self.num_sitewide_threads = total_threads
        self.num_sitewide_total_posts = total_posts
        # not fully sure of logic behind distinct post and total posts
        self.num_sitewide_dist_posts += dist_posts

    # Helper function for setting site values:
    def calculate_total_posts(self, master_version: str) -> int:
        """Calculates total number of posts within a given master thread"""
        with open(master_version, "r") as json_file:
            master = json.load(json_file)
            replies: dict = master["replies"]
            num_of_replies: int = len(replies.keys())
        json_file.close()
        total_posts = num_of_replies + 1  # the added 1 accounts for the OP
        return total_posts

    def get_thread_meta(self):
        """Returns a dictionary for a JSON file of dist_post_ids, lost_post_ids, num_dist_posts
        num_total_posts, num_lost_posts"""
        return {
            "dist_post_ids": list(self.dist_post_ids),
            "lost_post_ids": list(self.lost_post_ids),
            "num_dist_posts": self.num_dist_posts,
            "num_total_posts": self.num_total_posts,
            "num_lost_posts": self.num_lost_posts
        }

    def get_scan_meta(self):
        """Returns a dictionary for a JSON file of all_post_ids, new_post_ids, new_lost_posts
        num_all_posts, num_new_posts, num_new_lost_posts"""
        return {
            "all_post_ids": list(self.all_post_ids),
            "new_post_ids": list(self.new_post_ids),
            "new_lost_posts": list(self.new_lost_posts),
            "num_all_posts": self.num_all_posts,
            "num_new_posts": self.num_new_posts,
            "num_new_lost_posts": self.num_new_lost_posts
        }

    def get_site_meta(self):
        """Returns a dictionary for a JSON file of num_sitewide_threads, num_sitewide_total_posts, num_sitewide_dist_posts"""
        return {
            "num_sitewide_threads": self.num_sitewide_threads,
            "num_sitewide_total_posts": self.num_sitewide_total_posts,
            # "num_sitewide_dist_posts": self.num_sitewide_dist_posts
        }

    # TODO: new_thread is no longer needed; will later clean this up + calls to it in other functs
    def update_site_meta(self, new_thread):
        """Call after setting scan and thread values; accesses and updates site meta file with appropriate stats from
        get_site_meta()"""
        site_meta = "./data/crystal.cafe/" + self.site_title + "_meta.json"

        with open(site_meta, 'r+') as site_json_file:
            site_data = json.load(site_json_file)
            self.set_site_values()
            # Update existing values and add new ones
            site_data.update(self.get_site_meta())
            site_json_file.seek(0)
            json.dump(site_data, site_json_file, indent=4)
            site_json_file.truncate()
