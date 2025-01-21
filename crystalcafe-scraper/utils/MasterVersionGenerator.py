from datetime import datetime
from string import Template
from bs4 import BeautifulSoup
from utils import MetaStatHandler
import json
import os


class MasterVersionGenerator:
    # TODO: might have to change params depending on where funct is utilized; most likely will have to be used in Process to be in outer file
    def __init__(self, original, replies, thread_meta, id, folder_path):
        # Thread contents
        self.original = original
        self.replies = replies
        self.meta = thread_meta

        # File directory info
        self.thread_number = id
        self.folder_path = folder_path
        self.file_name = f"master_version_{self.thread_number}.json"
        self.file_path = os.path.join(self.folder_path, self.file_name)

        # Retrieves distinct post ids from thread meta
        distinct_reply_ids = thread_meta.get("dist_post_ids")

        # Adds ids to a set to ensure no duplication.
        self.thread_post_ids = set(distinct_reply_ids)

    def add_to_set(self, thread_replies):
        """Adds original post and replies to a set to preserve deleted posts"""
        for reply in thread_replies:
            self.thread_post_ids.add(reply["post_id"])

    def generate_dict(self):
        """Generates a dictionary containing all posts on a given thread"""
        current_time = datetime.today().strftime("%Y-%m-%dT%H:%M:%S")
        thread_replies = self.replies.values()
        self.add_to_set(thread_replies)
        all_replies = {}

        thread_contents = {
            "date_of_previous_scan": "",
            "date_of_latest_scan": current_time,
            "thread_number": self.thread_number,
            "original_post": self.original,
        }

        # Add replies with ids recorded in set in order to prevent duplication.
        for reply in thread_replies:
            reply_id = reply["post_id"]
            if reply_id in self.thread_post_ids:
                all_replies[reply_id] = reply

        # Updates scan times
        previous_scan_time = thread_contents.get("date_of_latest_scan")
        thread_contents.update({"date_of_previous_scan": previous_scan_time})
        thread_contents.update(
            {"date_of_latest_scan": datetime.today().strftime("%Y-%m-%dT%H:%M:%S")}
        )

        # Updates replies
        thread_contents.update({"replies": all_replies})
        return thread_contents

    def write_master_thread(self):
        """Opens a writeable text file, writes related headers and original post content on it and then closes file."""
        try:
            with open(self.file_path, "r") as f:
                existing_data = json.load(f)
        except FileNotFoundError:
            # Initialize with empty replies if file doesn't exist
            existing_data = {"replies": {}}

        # Generate the updated thread dictionary
        thread_contents = self.generate_dict()

        # Merge existing replies with new replies
        existing_replies = existing_data.get("replies", {})
        thread_contents["replies"].update(existing_replies)

        # Write the updated data to the file
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(thread_contents, f, indent=3, ensure_ascii=False)
