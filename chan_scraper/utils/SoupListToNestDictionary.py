# Imports
import copy
import re

from bs4 import BeautifulSoup
from htmldate import find_date

class SoupListToNestDictionary:
    """Populates and updates a nested dictionary per BeautifulSoup object."""
    def soup_list_to_nest_dictionary(
            self, soup_list: list[BeautifulSoup], nested_dictionary, 
            scrape_dir: str, scan_time: str, op_class: str,
            op_id_prefix: str, reply_class: str, reply_id_prefix: str,
            ):
        """Updates/saves a nested dictionary with each BeautifulSoup object.

        Each BeautifulSoup object is used to update current_scrape data
        and thread_meta data in the nested dictionary. Then, JSON files are
        saved for each thread's thread_meta file and each thread's current
        scan meta file.

        TODO: Change so structure goes 
        SoupListToNestDictionary → NestDictionaryToMeta (thread_meta, 
            site_meta, scrape_meta)

        TODO: For guidelines, have docs require Args, Params, etc. if
        under class or main methods

        Args:
            soup_list: List of BeautifulSoup objects.
            nested_dictionary: Initialized nested dictionary.
            scan_time: Time of scan.
            scrape_dir: Directory for scrape data.
            op_class: Name of class for original posts.
            op_id_prefix: Prefix for IDs of original posts (can be empty).
            reply_class: Name of class for post replies.
            reply_id_prefix: Prefix for IDs of replies.
        """
        # Each batch of URLs/BeautifulSoup objects can have multiple instances
        # of the same thread. Each duplicate URL will lead to the same,
        # up-to-date instance of a thread. Therefore, if a thread has been
        # scraped once, it doesn't need to be scraped again. There will not
        # be more than
        thread_set: set[str] = []  

        new_dictionary = nested_dictionary.deepcopy()  # TODO: Confirm works
        
        for soup in soup_list:
            thread_number = soup.find(class_="intro").get("id")
            if thread_number not in thread_set:
                thread_set.add(thread_number)

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
                dist_posts = (nested_dictionary[thread_number]\
                    ["thread_meta"]["dist_post_ids"])
                for post_id in all_posts:
                    if post_id not in dist_posts:
                        new_posts.append(post_id)
                        new_dist_posts.append(post_id)
                
                # Get posts that were once in dist_post_ids, but are not
                lost_posts = (nested_dictionary[thread_number]\
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
                    thread_number, thread_data, scrape_data, new_dictionary)

        return new_dictionary

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
            self, thread_number, thread_data, scrape_data, new_dictionary):
        pass
    # def write_data(self, current_scrape_data):
    #     # if is_thread_meta:
    #     #     self.stat_handler.set_scan_and_thread_values(self.soup)
    #     #     self.stat_handler.update_site_meta(True)
    #     #     metadata = {**self.page_info_to_JSON(), **self.date_to_JSON(), **self.stat_handler.get_thread_meta()}   
    #     # else:
    #     #     self.stat_handler.set_scan_and_thread_values(self.soup)
    #     #     self.stat_handler.update_site_meta(False)
    #     #     metadata = {**self.page_info_to_JSON(), **self.date_to_JSON(), **self.stat_handler.get_scan_meta()}

    #     # with open(self.file_path, "w", encoding="utf-8") as f:
    #     #     json.dump(metadata, f, indent=2, ensure_ascii=False)
    #     pass