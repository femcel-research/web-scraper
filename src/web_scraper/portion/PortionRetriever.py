import datetime
import json
import os
import random
import glob
import math
from string import Template
from datetime import datetime
import argparse


class PortionRetriever:
    """Returns a portion of threads as a folder containing .txt files. Enter percentage as a whole number (i.e enter 15% as 15)"""

    def __init__(self, thread_percentage, site_name):
        self.used_ids = set()  # Used to ensure no repetition in portions
        self.thread_percent = thread_percentage / 100
        self.data_folder_path = "./data/"
        # name of site subfolder in data (i.e crystal.cafe data subfolder is titled crystalcafe)
        self.site_dir_name = site_name
        self.scan_time = datetime.today().strftime("%Y-%m-%dT%H:%M:%S")

        txt_name = f"{self.site_dir_name}_list_of_used_threads.txt"
        self.used_threads_txt = os.path.join(
            self.data_folder_path, "thread_portion", txt_name)

        if os.path.exists(self.used_threads_txt):
            # Ensures used_ids set is updated
            self.read_used_thread_ids_from_txt()
        else:
            # Creates file
            open(self.used_threads_txt, "w").close()

    # Helper functions:

    def total_num_of_threads(self) -> int:
        """Generates number of threads based off of the number of sitewide threads recorded in the site_meta.json."""
        # Meta stat retrieval:
        site_meta_path = (
            # Search for site meta file
            f"./data/{self.site_dir_name}/{self.site_dir_name}_meta.json"
        )
        with open(site_meta_path, "r") as file:  # Fetch meta file
            site_meta = json.load(file)

        # Get total number of threads
        sitewide_threads = site_meta["num_sitewide_threads"]
        return sitewide_threads

    def generate_portion_folder_path(self) -> str:
        """Creates a thread_portion folder."""
        folder_name = "thread_portion"
        # Portion folder path:
        folder_path = os.path.join(
            self.data_folder_path, folder_name, self.site_dir_name, self.scan_time)

        try:
            os.makedirs(folder_path, exist_ok=True)
            print(f"Directory '{folder_name}' created successfully.")

        except FileExistsError:
            print(f"Directory '{folder_name}' already exists.")

        return folder_path

    def generate_txt(self, portion_folder_path: str, thread_id: int) -> str:
        """Generates corresponding .txt filepath"""
        txt_filepath = os.path.join(
            portion_folder_path, f"thread_{thread_id}.txt")
        return txt_filepath

    def convert_thread_to_txt(self, thread_json_path: str, portion_folder_path: str):
        """Converts a given thread .json to a .txt file containing unique identifiers for each post (post id), post content, date posted, ids of replied posts."""
        try:
            with open(thread_json_path, "r") as file:  # Fetch meta file
                thread_contents = json.load(file)
        except FileNotFoundError:
            print(f"Error: JSON file not found at {thread_json_path}")
            return
        # Thread info:
        thread_id = thread_contents["thread_number"]
        original_post = thread_contents["original_post"]
        replies = thread_contents["replies"]

        with open(self.generate_txt(portion_folder_path, thread_id), "w") as file:
            # Orignal Post Info:
            og_post_id = original_post["post_id"]
            og_date = original_post["date_posted"]
            og_content = original_post["post_content"]
            replied_thread_ids = original_post["replied_thread_ids"]
            file.write(
                f"Thread_Number: {thread_id} \n Original_Post_ID: {og_post_id} \n Date_Posted: {og_date} \n Post_Content: {og_content} \n Replied_Thread_IDs: {replied_thread_ids} \n")

            # Reply Info:
            for reply in replies.values():
                post_id = reply["post_id"]
                date = reply["date_posted"]
                post_content = reply["post_content"]
                replied_post_ids = reply["ids_of_replied_posts"]
                file.write(
                    f"Post_ID: {post_id} \n Date_Posted: {date} \n Post_Content: {post_content} \n Replied_Post_IDs: {replied_post_ids}\n")
        file.close()

    def write_used_thread_ids_to_txt(self):
        """Writes all used thread IDs to a .txt file. Done to prevent selecting used threads when providing randomized portions. Returns a filepath to the .txt file."""
        # Get path for file containing a list of used thread ids
        with open(self.used_threads_txt, "w") as file:
            for id in sorted(self.used_ids):
                file.write(f"{id}\n")

    def read_used_thread_ids_from_txt(self):
        """Reads used thread IDs from a .txt file (one ID per line). Done to prevent selecting used threads when providing randomized portions. Returns a set containing integer values representing thread IDs."""
        self.used_ids = set()
        try:
            with open(self.used_threads_txt, "r") as file:
                # Ensures no duplication
                for line in file:
                    stripped = line.strip()
                    if stripped:
                        try:
                            self.used_ids.add(int(stripped))
                        except ValueError:
                            print(
                                f"Skipping invalid thread ID '{stripped}' (not an integer)")
            file.close()
        except FileNotFoundError:  # Handle cases where the file does not exist
            print(f"File not found: {self.used_threads_txt}")

    def random_thread_folder(self, directory: str) -> str:
        """Given a directory, it will return a random folder from that directory."""
        folder_path = random.choice(os.listdir(directory))
        return folder_path

    def thread_master_retrieval(self, folder_path: str) -> str:
        """Returns the master version of a given thread folder."""
        # Pattern search for master version
        master_search = os.path.join(
            folder_path, 'master_version_*.json')

        # Iterate through files that match the pattern search
        for file in glob.glob(master_search):
            master_version_path = os.path.abspath(file)
            return master_version_path
        return None

    def add_to_portion(self, master_thread_path: str, portion_folder_path: str) -> bool:
        """Adds master thread to portion."""
        try:
            with open(master_thread_path, "r") as file:
                master_thread = json.load(file)
            thread_id = int(master_thread["thread_number"])
        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            print(f"Error processing {master_thread_path}: {str(e)}")
            return False
        if thread_id in self.used_ids:
            return False

        # Convert thread to txt
        self.convert_thread_to_txt(master_thread_path, portion_folder_path)

        # Mark thread as used
        self.used_ids.add(thread_id)

        return True

    def generate_randomized_portion(self):
        """Generates and outputs a randomized portion of the data."""
        folder_path = os.path.join(self.data_folder_path, self.site_dir_name)
        # Number of threads is determined by percentage inputted
        num_of_threads = math.ceil(
            self.total_num_of_threads() * self.thread_percent)
        portion_folder_path = self.generate_portion_folder_path()
        successful_threads = 0

        # Continue until we have reached [PERCENTAGE] amount of threads
        while successful_threads < num_of_threads:
            thread_folder = self.random_thread_folder(folder_path)
            thread_path = os.path.join(folder_path, thread_folder)
            master_thread_path = self.thread_master_retrieval(thread_path)
            if master_thread_path and self.add_to_portion(master_thread_path, portion_folder_path):
                # If we successfully add a thread to the portion, then increment.
                successful_threads += 1
        self.write_used_thread_ids_to_txt()

    def generate_all(self):
        """Generates and outputs portion consisting of all collected data."""
        directory = os.path.join(self.data_folder_path, self.site_dir_name)
        portion_folder_path = self.generate_portion_folder_path()

        # Iterates through all thread folders in directory
        for dirpath, dirnames, filenames in os.walk(directory):
            master_thread_path = self.thread_master_retrieval(dirpath)
            if master_thread_path:
                self.add_to_portion(master_thread_path,
                                    portion_folder_path)
        self.write_used_thread_ids_to_txt()


if __name__ == "__main__":  # used to run script as executable
    parser = argparse.ArgumentParser(
        description="Generate a portion of threads.")
    parser.add_argument("thread_percentage", type=int,
                        help="Percentage of threads to retrieve (e.g., 10 for 10%)")
    parser.add_argument("site_name", type=str,
                        help="Name of the site (e.g., crystal.cafe)")
    parser.add_argument("randomization", type=int,
                        help="True for randomized portion, False for generating a portion consisting of all collected data.")
    args = parser.parse_args()
    retriever = PortionRetriever(args.thread_percentage, args.site_name)

    if (args.randomization == 1):
        retriever.generate_randomized_portion()

    if (args.randomization == 0):
        retriever.generate_all()
