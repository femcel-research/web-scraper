from datetime import datetime
import json
from string import Template
from bs4 import BeautifulSoup
from utils.processing.meta_handling.MetaStatHandler import MetaStatHandler
import logging
import os


class MasterVersionGenerator:
    # new version
    #TODO move logging to diff part of pipeline or use logger as arg?
    def __init__(self, thread_contents_json, thread_meta, id, folder_path):
        # File directory info
        self.thread_number = id
        self.folder_path = folder_path
        self.file_name = f"master_version_{self.thread_number}.json"
        self.file_path = os.path.join(self.folder_path, self.file_name)
        self.scan_time = datetime.today().strftime("%Y-%m-%dT%H:%M:%S")

        # Thread content
        self.thread_contents = thread_contents_json
        self.original_post = self.thread_contents["original_post"]
        self.replies = self.thread_contents["replies"]

        # Lost post id retrieval
        self.thread_meta = thread_meta
        lost_ids = thread_meta["lost_post_ids"]

        self.lost_ids_set = set(lost_ids)

        # Master version generation logging
        log_dir = "./data/crystal.cafe/logs/master-thread-logs"
        os.makedirs(log_dir, exist_ok=True)
        master_log_filename = os.path.join(log_dir, f"{self.scan_time}.log")

        self.master_logger = logging.getLogger('Master_Thread')
        self.master_logger.setLevel(logging.INFO)
        
        #TODO: fix logging for master vers gen.
        
        #File handler
        master_handler = logging.FileHandler(master_log_filename, mode='w')

        #Log formatter
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s", 
            datefmt="%Y-%m-%dT%H:%M:%S"
        )
        master_handler.setFormatter(formatter)

        #Log handler
        self.master_logger.addHandler(master_handler)

    def check_if_post_lost(self, post_id):
        """Checks if given post was deleted"""
        if post_id in self.lost_ids_set:
            logging.info(f"Post ID {post_id} was deleted from the original thread")
            return True
        return False

    def generate_dict(self):
        """Generates a dictionary containing all posts on a given thread"""
        all_replies = {}

        thread_contents = {
            "date_of_previous_scan": "",
            "date_of_latest_scan": "",
            "thread_number": self.thread_number,
            "original_post": self.original_post,
        }
        
        # Updates scan times
        previous_scan_time = thread_contents["date_of_latest_scan"]
        thread_contents.update({"date_of_previous_scan": previous_scan_time})
        self.master_logger.debug(f"Date of previous scan has been updated to: {previous_scan_time}")

        current_time = datetime.today().strftime("%Y-%m-%dT%H:%M:%S")
        thread_contents.update({"date_of_latest_scan": current_time})
        self.master_logger.debug(f"Date of latest scan has been updated to: {current_time}")
        
        # Adds deletion marker if needed
        for reply in self.replies.values():
            reply_id = reply.get("post_id")
            if self.check_if_post_lost(reply_id):
                reply.update({"post_lost": self.check_if_post_lost(reply_id)})
            all_replies[reply_id] = reply
            logging.info(f"Reply {reply_id} has been added to the master thread.")

        # Updates replies
        thread_contents.update({"replies": all_replies})
        self.master_logger.info("Updated replies.")
        return thread_contents

    def write_master_thread(self):
        """Opens a writeable text file, writes related headers and original post content on it and then closes file."""
        try:
            with open(self.file_path, "r") as f:
                existing_data = json.load(f)
                self.master_logger.info(
                    f"Openining existing master thread for thread #{self.thread_number}"
                )
        except FileNotFoundError:
            # Initialize with empty replies if file doesn't exist
            self.master_logger.info(
                f"Master thread does not exist for thread #{self.thread_number}"
            )
            existing_data = {"replies": {}}
            self.master_logger.info(f"Master thread created for thread #{self.thread_number}")

        # Generate the updated thread dictionary
        thread_contents = self.generate_dict()

        # Merge existing replies with new replies
        existing_replies = existing_data["replies"]
        thread_contents["replies"].update(existing_replies)
        self.master_logger.info(
            f"Master thread replies for thread #{self.thread_number} are up to date."
        )

        # Write the updated data to the file
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(thread_contents, f, indent=3, ensure_ascii=False)
