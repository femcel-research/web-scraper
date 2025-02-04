from datetime import datetime
from string import Template
from bs4 import BeautifulSoup
from utils import MetaStatHandler
import json
import os


class MasterVersionGenerator:
    # new version
    def __init__(self, thread_contents_json, thread_meta, id, folder_path):
        # File directory info
        self.thread_number = id
        self.folder_path = folder_path
        self.file_name = f"master_version_{self.thread_number}.json"
        self.file_path = os.path.join(self.folder_path, self.file_name)

        # Thread content
        self.thread_contents = thread_contents_json
        self.original_post = self.thread_contents["original_post"]
        self.replies = self.thread_contents["replies"]

        # Lost post id retrieval
        self.thread_meta = thread_meta
        lost_ids = thread_meta["lost_post_ids"]

        self.lost_ids_set = set(lost_ids)

    def check_if_post_lost(self, post_id):
        """Checks if given post was deleted"""
        if post_id in self.lost_ids_set:
            return True
        return False

    def generate_dict(self):
        """Generates a dictionary containing all posts on a given thread"""
        current_time = datetime.today().strftime("%Y-%m-%dT%H:%M:%S")
        all_replies = {}

        thread_contents = {
            "date_of_previous_scan": "",
            "date_of_latest_scan": current_time,
            "thread_number": self.thread_number,
            "original_post": self.original_post,
        }

        # Adds deletion marker if needed
        for reply in self.replies.values():
            reply_id = reply.get("post_id")
            if self.check_if_post_lost(reply_id):
                reply.update({"post_lost": self.check_if_post_lost(reply_id)})
            all_replies[reply_id] = reply

        # Updates scan times
        previous_scan_time = thread_contents["date_of_latest_scan"]
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
        existing_replies = existing_data["replies"]
        thread_contents["replies"].update(existing_replies)

        # Write the updated data to the file
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(thread_contents, f, indent=3, ensure_ascii=False)
