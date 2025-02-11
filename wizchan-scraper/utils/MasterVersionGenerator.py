from datetime import datetime
from string import Template
from bs4 import BeautifulSoup
from utils import MetaStatHandler
import json
import os


class MasterVersionGenerator:
    #TODO: might have to change params depending on where funct is utilized; most likely will have to be used in Process to be in outer file
    def __init__(self, original, replies, thread_number, folder_path):
        # Website info
        self.original = original
        self.replies = replies
        self.folder_path = folder_path
        self.thread_number = thread_number
        self.file_name = "master_version_" + self.threadNumber + ".json"
        self.file_path = os.path.join(self.folder_path, self.file_name)

    def get_set_contents(self):
        """Returns the set of post_ids"""
        thread_set = set(())
        return thread_set

    def add_to_set(self, original_post, replies):
        """Adds original post and replies to a set to preserve deleted posts"""
        id_set = self.get_set_contents()
        id_set.update(original_post["post_id"])

        for reply in replies.values():
            id_set.update(reply["post_id"])

    def generate_dict(self):
        """Generates a dictionary containing all posts on a given thread"""
        id_set = self.get_set_contents
        original_post_id = self.original["post_id"]
        replies = {}
        
        thread_contents = {
            "thread_number": self.thread_number,
        }

        if id_set.issubset(original_post_id):
            thread_contents.update({"original_post": self.original})

        for reply in self.replies.values():
            if id_set.issubset(reply["post_id"]):
                replies[reply["post_id"]] = reply

        thread_contents.update({"replies": replies})
        return thread_contents

    def write_thread(self):
        """Opens a writeable text file, writes related headers and original post content on it and then closes file."""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.generate_dict(), f, indent=3, ensure_ascii=False)
