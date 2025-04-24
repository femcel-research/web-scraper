import json
from pathlib import Path


class StatCollector:
    """ Parent class with methods relating to the collection of posts and post IDs."""

    def __init__(self):
        """Generalized methods for stat collection"""
        self.new_post_ids = set()
        self.all_post_ids = set()
        self.distinct_post_ids = set()
        self.sitewide_lost_post_ids = set()
        self.sitewide_new_lost_ids = set()
        self.num_total_posts = 0

        # Distinct post ids
    def collect_post_ids(self, content_file: str) -> set:
        """Collects all post ids within a specified file"""
        with open(content_file, "r") as json_file:
            thread = json.load(json_file)
            replies: dict = thread["replies"]
            self.distinct_post_ids.add(thread["thread_number"])
            self.distinct_post_ids.update(replies.keys)
        json_file.close()
        return self.distinct_post_ids

    def collect_all_post_ids(self, thread_folder: str) -> set:
        """Collects all thread ids within a given thread"""
        directory = Path(thread_folder)
        if not directory.is_dir():
            print(f"Error: Directory not found: {directory}")
            return
        for subfolder in directory.iterdir():
            # if the folder is not a directory then its not a scan folder
            if not subfolder.is_dir:
                print(
                    f"Listed item in directory is not an older scan of a thread: {subfolder.name}")
                continue
            else:
                # there should be one content json per scan folder
                results = subfolder.glob("content_*.json")
                content = results[0]
                post_ids = self.collectPostIDs(content)
                self.all_post_ids.update(post_ids)
        return self.all_post_ids

    # Num total posts
    def calculate_total_posts(self, master_version: str) -> int:
        """Calculates total number of posts within a given master thread"""
        with open(master_version, "r") as json_file:
            master = json.load(json_file)
            replies: dict = master["replies"]
            num_of_replies: int = len(replies.keys())
        json_file.close()
        total_posts = num_of_replies + 1
        self.num_total_posts += total_posts  # the added 1 accounts for the OP
        return self.num_total_posts

    # Lost posts
    def collect_lost_posts(self, distinct_ids: set, master_version: str) -> set:
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
        return self.sitewide_lost_post_ids

    def collect_new_posts(self, distinct_ids: set, master_version: str) -> set:
        """Collects new post ids from the master version and populates them into a set."""
        new_posts = set()
        master_post_ids = self.collect_all_post_ids(master_version)
        for post_id in master_post_ids:
            if post_id not in distinct_ids:
                distinct_ids.add(post_id)
                new_posts.add(post_id)
        self.new_post_ids.update(new_posts)
        return self.new_post_ids
