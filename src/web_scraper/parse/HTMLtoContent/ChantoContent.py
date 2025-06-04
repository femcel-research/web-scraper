# Imports
import json
import logging
import os
import re

from bs4 import BeautifulSoup
from datetime import datetime

from .exceptions import ThreadIDNotFoundError, ContentInitError


class ChanToContent:
    """Takes HTML from a chan-style thread and formats it (to a JSON)."""
    def __init__(
            self, scrape_time: datetime,
            thread_soup: BeautifulSoup, site_dir: str,
            op_class: str, reply_class: str, url: str,
            post_date_location: str):
        """Given the HTML for a chan-style thread, a formatted JSON is made.
        
        All of the data which will be needed to calculate statistics,
        generate/track metadata, and create a readable and annotate-able text
        document is extracted from the HTML for a chan-style thread snapshot
        (which is passed on initialization). That data is formatted according
        to the "Snapshot Content File Data" standards in this project's 
        documentation.

        To ensure compatibility with various chan-style website threads,
        parameters are used to locate different information.

        Expect the parameters for different chan-style websites to be located
        in the params/ directory within the web-scraper project.

        Args:
            scrape_time (datetime): Time of scrape.
            thread_soup (BeautifulSoup): HTML from a thread in a soup object.
            site_dir (str): Directory for content files.
            op_class (str): Name of class for original posts.
            reply_class (str): Name of class for post replies.
            url (str): Used as a prefix in image URLs.
            post_date_location (str): Class/label string for date and time.
        """
        self.logger = logging.getLogger(__name__)

        self.scrape_time = scrape_time
        self.thread_soup = thread_soup
        self.site_dir = site_dir
        self.op_class = op_class
        self.reply_class = reply_class
        self.url = url
        self.post_date_location = post_date_location

        self.logger.info("Beginning the process of extracting content data " \
            "from a soup object.")
        try:
            self.thread_id: str = self.get_thread_id()
        except Exception as error:
            self.logger.error(f"Error when trying to initialize: {error}")
            raise ContentInitError(
                f"Error when trying to initialize: {error}") from error

    def get_thread_id(self):
        """Extracts a thread ID from the soup object from initialization.
        
        Raises:
            ThreadIDNotFoundError: If a thread ID cannot be found.
        """
        self.logger.info(f"Searching for a thread ID")
        thread_id = self.thread_soup.find(class_="intro").get("id")
        if thread_id is None:
            try:
                thread_id = self.thread_soup.find(class_="intro").find("a")\
                    .get("id").replace("post_no_", "")
                self.logger.info(f"ID successfully found: {thread_id}")
                return thread_id
            except:
                self.logger.error("Thread ID unable to be located")
                raise ThreadIDNotFoundError("Thread ID unable to be located")
        else:
            self.logger.info(f"ID successfully found: {thread_id}")
            return thread_id

    def extract_images(self, post, url):
            """Extracts image links from a given post and returns an array.
            
            Args:
                post            
            """
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
        post_date = post.find(class_=post_date_location)
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
    
    def extract_original_post(
            self, original_post, url, post_date_location, thread_number):
        """Outputs content from original post as a dictionary."""
        op_id = original_post.find(class_="intro").get("id")
        if op_id is None:
            op_id = thread_number
        date = self.extract_datetime(original_post, post_date_location)
        original_post_body = original_post.find(class_="body")
        links_to_other_posts = self.extract_replied_posts_ids(
            original_post_body)
        links = []

        original_content = {
            "post_id": 
                op_id,
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
            reply_id = reply.find(class_="intro").get("id")
            if reply_id is None:
                reply_id = reply.get("id").replace("reply_", "")
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
                    reply_id,
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
            original_post, url, post_date_location, thread_number)
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