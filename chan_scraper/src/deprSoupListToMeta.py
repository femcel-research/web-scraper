# aggregate dict

# Take in a soup list,
# for each soup object,
#   make a dictionary of thread and current scrape
#   try to populate thread dict, else 0
#   collect data from current scrape, tallying thread, current dicts, and aggregate dict
#   write out thread and current dict

# if needed, return aggregate dict via getter
# aggregate dict can either replace site aggregate if re processing everything
# or can be used to increment site aggregate

# TODO: Make ThreadListToMeta, delete this

# Imports
import json
import os
import re

from bs4 import BeautifulSoup
from datetime import datetime
from htmldate import find_date
from pathlib import Path

class SoupListToMeta:
    """Saves a list of thread's data into individual and per-thread files."""
    def soup_list_to_meta(self, soup_list: list[BeautifulSoup], 
            scrape_dir: str, scan_time: str, op_class: str,
            op_id_prefix: str, reply_class: str, reply_id_prefix: str):
        """For each BeautifulSoup object, metadata is collected.
        
        Each metadata JSON is collected by thread ID number, to an internally
        specified file directory (based on arguments).

        Metadata is written to a file associated with the current scrape
        of metadata, as well as a file associated with the thread as a whole.
        Whole-thread metadata files are initialized with an existing file if
        one exists, then is updated according to current scrape metadata. Any
        existing whole-thread metadata file is overwritten with updated data.

        An additional aggregate dictionary keeps track of aggregate statistics
        which can be used as needed.

        Args:
            soup_list: List of BeautifulSoup objects.
            scan_time: Time of scan.
            scrape_dir: Directory for scrape data.
            op_class: Name of class for original posts.
            op_id_prefix: Prefix for IDs of original posts (can be empty).
            reply_class: Name of class for post replies.
            reply_id_prefix: Prefix for IDs of replies.

        """
        self.aggregate_dictionary = {}
        self.curr_soup_dictionary = {}
        self.empty_curr_soup_dictionary()

        # Each batch of URLs/BeautifulSoup objects can have multiple instances
        # of the same thread. Each duplicate URL will lead to the same,
        # up-to-date instance of a thread. Therefore, if a thread has been
        # scraped once, it doesn't need to be scraped again. Hence the set.
        thread_set: set[str] = set()

        for soup in soup_list:
            thread_number = soup.find(class_="intro").get("id")
            if thread_number is None:
                thread_number = soup.find(class_="intro").find("a")\
                    .get("id").replace("post_no_", "")
            if thread_number not in thread_set:
                # Get a master list of all posts
                all_posts = []
                original_post = soup.find(class_=op_class)
                all_posts.append(
                    original_post.find(class_="intro").get(
                        f"{op_id_prefix}id"))
                for reply in soup.find_all(class_=reply_class):
                    all_posts.append(
                        reply.find(class_="intro").get(
                            f"{reply_id_prefix}id"))
                    
                # Get posts that aren't already in dist_post_ids
                new_posts = []
                new_dist_posts = []
                dist_posts = (self.curr_soup_dictionary\
                    ["thread_meta"]["dist_post_ids"])
                for post_id in all_posts:
                    if post_id not in dist_posts:
                        new_posts.append(post_id)
                        new_dist_posts.append(post_id)
                
                # Get posts that were once in dist_post_ids, but are not
                lost_posts = (self.curr_soup_dictionary\
                    ["thread_meta"]["lost_post_ids"])
                new_lost_posts = []
                num_new_lost_posts = 0
                for post_id in dist_posts:
                    if post_id not in all_posts and\
                    post_id not in lost_posts:
                        new_lost_posts.append(post_id)
                        # TODO: Write to lost_posts
                        num_new_lost_posts += 1
                
                num_all_posts: int = len(all_posts)
                num_new_posts: int = len(new_posts)
                # TODO: Add all values to appropriate dictionaries 
                # self.num_dist_posts += self.num_new_posts
                # self.num_total_posts += self.num_all_posts
                # self.num_lost_posts += self.num_new_lost_posts
                # scrape_data = self.get_current_scrape_data(
                #     soup, scan_time, all_posts)
                # self.write_data(scrape_data)
                thread_data = {
                    **self.get_date_data(soup, scan_time),
                    **self.get_page_data(soup, thread_number),
                    }
                scrape_data = {}
                self.add_to_dictionary(
                    thread_number, thread_data, scrape_data)

    def empty_curr_soup_dictionary(self):
        self.curr_soup_dictionary = {
            "thread_meta": {
                "URL": "",
                "board": "",
                "thread_title": "",
                "thread_number": "",
                "date_published": "",
                "date_updated": "",
                "date_scraped": "",
                "dist_posts": [],
                "lost_posts": [],
                "num_dist_posts": 0,
                "num_total_posts": 0,
                "num_lost_posts": 0,
                "num_tokens": 0,  # TODO: New; implement
                "num_dist_tokens": 0  # TODO: New; implement
            },
            "current_scrape": {
                "URL": "",
                "board": "",
                "thread_title": "",
                "thread_number": "",
                "date_published": "",
                "date_updated": "",
                "date_scraped": "",
                "all_posts": [],
                "new_posts": [],
                "new_lost_posts": [],
                "num_all_posts": 0,
                "num_new_posts": 0,
                "num_new_lost_posts": 0,
                "num_tokens": 0,  # TODO: New; implement
                "num_dist_tokens": 0  # TODO: New; implement  
            }
        }

    def initialize_curr_soup_dictionary(self, scrape_dir: str, thread_number):
        """The current dictionary is initialized with prior thread_meta files.

        If a thread_meta file exists for a thread from a previous scrape, then
        the values from that thread_meta file will be used to initialize
        the thread_meta dictionary for the current BeautifulSoup object.

        Args:
            scrape_dir: Directory for scrape data.
            thread_number: Thread ID number.
        """
        thread_meta_path = Path(f"{scrape_dir}{thread_number}{os.sep}thread_meta_{thread_number}")
        if thread_meta_path.exists():
                with open(thread_meta_path, "r") as thread_meta:
                    meta = json.load(thread_meta)
                    for k in meta:  # For key in meta
                         if k in self.curr_soup_dictionary["thread_meta"]:
                              self.curr_soup_dictionary["thread_meta"][k] = (
                                   meta[k])
        else:
            pass  # TODO: Log
    
    def get_date_data(self, soup: BeautifulSoup, scan_time):
        """Captures date published, date updated, and date scraped."""
        date_published = find_date(
            str(soup), extensive_search=True, original_date=True,
            outputformat="%Y-%m-%dT%H:%M:%S")
        date_updated = find_date(
            str(soup), extensive_search=False, original_date=False,
            outputformat="%Y-%m-%dT%H:%M:%S")
        date_data = {
            "date_published": date_published,
            "date_updated": date_updated,
            "date_scraped": scan_time,
        }
        return date_data
    
    def get_page_data(self, soup: BeautifulSoup, thread_number):
        """Captures page URL, title, description, keyword, and site info."""
        page_title = soup.title.string
        board_and_title = re.split('[-]',page_title)
        for x in range(len(board_and_title)):
            board_and_title[x] = board_and_title[x].strip()
        board = board_and_title[0]
        title = board_and_title[1]
        page_data = {
            "URL": soup.url,
            "board": board,
            "thread_title": title,
            "thread_number": thread_number,
        }
        return page_data
    
    def add_to_dictionary(
            self, thread_number, thread_data, scrape_data):
        pass

    def get_aggregate_dictionary(self):
        return self.aggregate_dictionary
