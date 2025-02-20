# Imports
import json
import os
import re

from bs4 import BeautifulSoup
from datetime import datetime

class SoupListToContent:
    """Collects a list of URL's thread data into individual files."""
    def soup_list_to_content(
            self, soup_list: list[BeautifulSoup], scan_time: str, 
            scrape_dir: str, op_class: str, reply_class: str,
            url: str, post_date_location: str):
        """For each BeautifulSoup object, thread content is collected.
        
        Each content JSON is collected by thread ID number, to an internally
        specified file directory (based on arguments).

        Args:
            soup_list: List of BeautifulSoup objects.
            scan_time: Time of scan.
            scrape_dir: Directory for scrape data.
            op_class: Name of class for original posts.
            reply_class: Name of class for post replies.
            url: Used as a prefix in image URLs.
            post_date_location: Class/label string for datetime.
        """
        # Each batch of URLs/BeautifulSoup objects can have multiple instances
        # of the same thread. Each duplicate URL will lead to the same,
        # up-to-date instance of a thread. Therefore, if a thread has been
        # scraped once, it doesn't need to be scraped again.
        thread_set: set[str] = []  
        for soup in soup_list:
            if thread_number not in thread_set:
                thread_set.add(thread_number)
                thread_number = soup.find(class_="intro").get("id")
                content_file_name = f"content_{thread_number}.json"
                content_file_path = f"{scrape_dir}\
                    {thread_number}{os.sep}{scan_time}\
                    {os.sep}{content_file_name}"
                # Original post
                original_post = soup.find(class_=op_class)
                # Set of every page element with the class "post reply"
                post_replies = soup.find_all(class_=reply_class)
                with open(content_file_path, "w", encoding="utf-8") as file:
                    json.dump(
                        self.get_thread_contents(
                            thread_number, original_post, post_replies, 
                            url, post_date_location),
                        file, indent=3, ensure_ascii=False)

    def extract_images(self, post, url):
        """Extracts image links from a given post and returns an array."""
        image_links = []

        # For each image tag in a given post, get it's source and 
        # add it to the list of image links
        for image in post.find_all("img", class_="post-image"):
            src = image.get("src")
            if src:
                image_links.append(f"{url}{src}")
        return image_links
    
    def extract_text(self, post):
        """Extracts text from a given post and returns it as a string."""
        return post.get_text()
    
    def extract_datetime(self, post, post_date_location):
        """Extracts datetime from a given post."""
        # TODO: May not work as intended, maybe modify
        try:
            post_date = post.find(class_=post_date_location)
        except:
            pass
        else:
            post_date = post.find(label_for=post_date_location)
        datetime_str = post_date.find("time")["datetime"]

        # Converts post date to a datetime object
        dt_obj = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%SZ")

        # Formats object to be more uniform
        formatted_dt = dt_obj.strftime("%Y-%m-%dT%H:%M:%S")
        return formatted_dt
    
    def extract_replied_posts_ids(self, post):
        """Extracts the ID of a post a user replies to."""
        links_to_other_posts = post.find_all(
            "a", attrs={"href": re.compile("^/")})
        # Array that houses reply ids to other posts
        links = []
        for link in links_to_other_posts:
            links.append(link.text.strip().replace(">>", ""))

        return links

    def extract_original_post(self, original_post, url, post_date_location):
        """Outputs content from original post as a dictionary."""
        date = self.extract_datetime(original_post, post_date_location)
        original_post_body = original_post.find(class_="body")
        links_to_other_posts = self.extract_replied_posts_ids(
            original_post_body)
        links = []

        original_content = {
            "post_id": 
                original_post.find(class_="intro").get("id"),
            "username": 
                original_post.find(class_="name").get_text()
                .strip().replace("\n", ""),
            "reply_to_another_thread?": 
                True if links_to_other_posts else False,
            "date_posted": 
                date,
            "image_links": 
                self.extract_images(original_post, url),
            "post_content": 
                " ".join(self.extract_text(original_post_body).split()),
        }

        # Removes double arrows from in-post reference to replied post
        if links_to_other_posts:
            for link in links_to_other_posts:
                links.append(link.strip().replace(">>", ""))

        # If the original post is a reply to a different thread, 
        # add new dictionary entry
        original_content["replied_thread_ids"] = links
        return original_content
    
    def extract_replies(self, post_replies, url, post_date_location):
        """Outputs replies as a dictionary"""
        replies = {}
        for reply in post_replies:
            date = self.extract_datetime(reply, post_date_location)
            reply_body = reply.find("div", class_="body")
            links = self.extract_replied_posts_ids(reply_body)

            # If there is no link to another post, content is as usual. 
            # Otherwise, strip the link from the text
            if links is not None:
                text = self.extract_text(reply_body)
                for link in links:
                    text = text.replace(">>" + link, "")
                content = " ".join(text.split())
            else:
                content = " ".join(self.extract_text(reply_body).split())

            # Dictionary housing reply content
            reply_content = {
                "post_id": 
                    reply.find(class_="intro").get("id"),
                "ids_of_replied_posts": 
                    links,
                "username": 
                    reply.find(class_="name").get_text()
                    .replace("\n", "").strip(),
                "date_posted": 
                    date,
                "image_links": 
                    self.extract_images(reply, url),
                "post_content": 
                    content,
            }
            replies[reply["id"]] = reply_content

        return replies
    
    def get_thread_contents(
            self, thread_number, original_post, post_replies, 
            url, post_date_location):
        """Returns thread contents as a JSON"""
        op = self.extract_original_post(
            original_post, url, post_date_location)
        replies = self.extract_replies(post_replies, url, post_date_location)

        thread_contents = {
            "thread_number": 
                thread_number,
            "original_post": 
                op,
            "replies": 
                replies,
        }

        return thread_contents

