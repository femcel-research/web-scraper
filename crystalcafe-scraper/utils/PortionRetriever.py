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
    #look up how to clean a folder

    def __init__(self, thread_percentage, site_name):       
        self.thread_percent = thread_percentage / 100
        self.data_folder_path = "./data/"
        self.site_dir_name = site_name #name of site subfolder in data (i.e crystal.cafe data subfolder is titled crystalcafe)
        self.scan_time = datetime.today().strftime("%Y-%m-%dT%H:%M:%S")
        
        txt_name = f"{self.site_dir_name}_list_of_used_threads.txt"
        
        self.used_threads_txt = os.path.join(self.data_folder_path, "thread_portion", txt_name)
        
    # Helper functions
    def generate_number_of_threads(self):
        '''Generates number of threads based off of the number of sitewide threads recorded in the site_meta.json.'''
        # Meta stat retrieval:
        site_meta_path = (
            f"./data/{self.site_dir_name}/{self.site_dir_name}_meta.json"  # Search for site meta file
        )
        #data/crystalcafe/crystal.cafe_meta.json
        with open(site_meta_path, "r") as file:  # Fetch meta file
            site_meta = json.load(file)

        # Generate number of threads
        sitewide_threads = site_meta[
            "num_sitewide_threads"
        ]  # Get total number of threads
        num_of_threads = (
            sitewide_threads * self.thread_percent
        )  # Multiply by thread percentage
        return num_of_threads
        
    def generate_portion_folder(self): 
        '''Creates a thread_portion folder.'''
        folder_name = "thread_portion"
        folder_path = os.path.join(self.data_folder_path, folder_name, self.site_dir_name, self.scan_time)
        #TODO: iron out pathing format
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path, exist_ok=True)
                print(f"Directory '{folder_name}' created successfully.")
            except FileExistsError:
                print(f"Directory '{folder_name}' already exists.")
        return folder_path
    
    def convert_thread_to_txt(self, thread_json, portion_folder_path):
        '''Converts a given thread .json to a .txt file containing unique identifiers for each post (post id), post content, date posted, ids of replied posts.'''
        thread_contents_path = thread_json
        try:
            with open(thread_contents_path, "r") as file:  # Fetch meta file
                thread_contents = json.load(file)
        except FileNotFoundError:
            print(f"Error: JSON file not found at {thread_contents_path}")
            return
        thread_id = thread_contents["thread_number"]
        original_post = thread_contents["original_post"]  
        replies = thread_contents["replies"]
        
        txt_filepath = os.path.join(portion_folder_path, f"thread_{thread_id}.txt")
        with open(txt_filepath, "w") as file:
            #Orignal Post Info:
            og_post_id = original_post["post_id"]
            og_date = original_post["date_posted"]
            og_content = original_post["post_content"]
            replied_thread_ids = original_post["replied_thread_ids"]
            
            file.write(f"Thread_Number: {thread_id} \n Original_Post_ID: {og_post_id} \n Date_Posted: {og_date} \n Post_Content: {og_content} \n Replied_Thread_IDs: {replied_thread_ids} \n")
            
            #Reply Info:
            for reply in replies.values():
                post_id = reply["post_id"]
                date = reply["date_posted"]
                post_content = reply["post_content"]
                replied_post_ids = reply["ids_of_replied_posts"]
                file.write(f"Post_ID: {post_id} \n Date_Posted: {date} \n Post_Content: {post_content} \n Replied_Post_IDs: {replied_post_ids}\n")
            file.close()
        
    # Write and read used thread IDs from a .txt file.
    def write_used_thread_ids_to_txt(self, thread_id):
        """Writes used thread IDs to a .txt file (one ID per line). Done to prevent selecting used threads when providing randomized portions. Returns a filepath to the .txt file."""
        #Get path for file containing a list of used thread ids
        with open(self.used_threads_txt, "a") as file:
                file.write(f"{thread_id} \n")
        return self.used_threads_txt
            
    def read_used_thread_ids_from_txt(self):
        """Reads used thread IDs from a .txt file (one ID per line). Done to prevent selecting used threads when providing randomized portions. Returns a set containing integer values representing thread IDs."""
        try:
            with open(self.used_threads_txt, "r") as f:
                used_ids = set(int(line.strip()) for line in f if line.strip()) # Ensures no duplication
                return used_ids
        except FileNotFoundError:
            return set()  # Return an empty set if the file doesn't exist
        except ValueError: # Handle cases where the file has non-integer values
            print("Invalid values in .txt file, please ensure all lines are integers")
            return set()     
    
    #Randomly select a thread and its thread master vers.
    def random_thread_folder(self, directory): #logic from https://stackoverflow.com/questions/701402/best-way-to-choose-a-random-file-from-a-directory
        '''Given a directory, it will return a random folder from that directory.'''
        folder = random.choice(os.listdir(directory))
        return folder
    
    def thread_master_retrieval(self, random_folder):
        '''Returns the master version of a given thread folder.'''
        folder_path = os.path.join(self.data_folder_path, self.site_dir_name, random_folder)
        potential_master_path = os.path.join(folder_path, 'master_version_*.json')
        for file in glob.glob(potential_master_path):
            master_version_path = os.path.abspath(file)
            return master_version_path
    
    #Generate portion w/ helpers above.
    def generate_portion(self):
        '''Generates and outputs portion of data.'''
        folder_path = os.path.join(self.data_folder_path, self.site_dir_name)
        num_of_threads = math.ceil(self.generate_number_of_threads())
        used_ids = self.read_used_thread_ids_from_txt()
        portion_folder_path = self.generate_portion_folder()
        successful_threads = 0
        while successful_threads < num_of_threads:
            thread_folder = self.random_thread_folder(folder_path)
            master_thread_path = self.thread_master_retrieval(thread_folder)
            if (master_thread_path is not None):
                with open(master_thread_path, "r") as file:  # Fetch meta file
                    master_thread = json.load(file)
                    thread_id = master_thread["thread_number"]
                    if (thread_id not in used_ids):
                        self.convert_thread_to_txt(master_thread_path, portion_folder_path)
                        self.write_used_thread_ids_to_txt(thread_id)
                successful_threads += 1
                
if __name__ == "__main__":  #used to run script as executable
    parser = argparse.ArgumentParser(description="Generate a portion of threads.")
    parser.add_argument("thread_percentage", type=int, help="Percentage of threads to retrieve (e.g., 10 for 10%)")
    parser.add_argument("site_name", type=str, help="Name of the site (e.g., crystal.cafe)")
    args = parser.parse_args()
    retriever = PortionRetriever(args.thread_percentage, args.site_name)
    retriever.generate_portion()          