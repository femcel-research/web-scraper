from datetime import datetime
from bs4 import BeautifulSoup
import requests
import json
import os
import re


class TextCollector:
    def __init__(self, soup, folder_path):

        # Creates a soup object.
        self.soup = soup

        # Returns top portion of original post
        self.threadIntro = soup.find(class_="intro")
        self.threadNumber = soup.find(class_="intro").get("id")

        # Returns original post.
        self.originalPost = soup.find(class_="post op")

        # Variable holds the ID of the original post.
        self.originalPostID = self.threadIntro["id"]

        # Finds every page element with the class "post reply" and returns it in an array.
        self.postReplies = soup.find_all(class_="post reply")
        
        # Directory variables
        self.folder_path = folder_path
        self.file_name = "content_" + self.threadNumber + ".json"
        self.file_path = os.path.join(self.folder_path, self.file_name)

    def extract_images(self, post):
        """Extracts image links from a given post and returns them as an array."""
        image_links = []

        # For each image tag in a given post, get it's source and add it to the list of image links.
        for image in post.find_all("img", class_="post-image"):
            src = image.get("src")
            if src:
                image_links.append("https://crystal.cafe" + src)
        return image_links

    def extract_text(self, post):
        """Extracts text from a given post and returns it as a string."""
        return post.get_text()

    def extract_datetime(self, post):
        """Extracts datetime from a given post"""
        post_date = post.find(class_="post_no date-link")
        datetime_str = post_date.find("time")["datetime"]

        # Converts post date to a datetime object
        dt_obj = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%SZ")

        # Formats object to be more uniform
        formatted_dt = dt_obj.strftime("%Y-%m-%dT%H:%M:%S")
        return formatted_dt

    def extract_original_post(self):
        """Outputs content from original post as a dictionary"""
        date = self.extract_datetime(self.originalPost)
        original_post_body = self.originalPost.find(class_="body")
        links_to_other_posts = self.extract_replied_posts_ids(original_post_body)
        links = []

        original_content = {
            "post_id": self.originalPost.find(class_="intro").get("id"),
            "username": self.originalPost.find(class_="name").get_text(),
            "reply_to_another_thread?": True if links_to_other_posts else False,
            "date_posted": date,
            "image_links": self.extract_images(self.originalPost),
            "post_content": self.extract_text(original_post_body),
        }

        # Removes double arrows from in-post reference to replied post
        if links_to_other_posts:
            for link in links_to_other_posts:
                links.append(link.strip().replace(">>", ""))

        # If the original post is a reply to a different thread, add new dictionary entry.
        original_content["replied_thread_ids"] = links
        return original_content

    def extract_replied_posts_ids(self, post):
        """Extracts the ID of a post a user replies to."""
        links_to_other_posts = post.find_all("a", attrs={"href": re.compile("^/")})
        # Array that houses reply ids to other posts.
        links = []
        for link in links_to_other_posts:
            links.append(link.text.strip().replace(">>", ""))

        return links

    def extract_replies(self):
        """Outputs replies as a dictionary"""
        replies = {}
        for reply in self.postReplies:
            date = self.extract_datetime(reply)
            reply_body = reply.find("div", class_="body")
            links = self.extract_replied_posts_ids(reply_body)

            # If there is no link to another post, content is as usual. Otherwise, strip the link from the text.
            if links is not None:
                text = self.extract_text(reply_body)
                for link in links:
                    text = text.replace(">>" + link, "")
                content = text.strip()
            else:
                content = self.extract_text(reply_body)

            # Dictionary housing reply content.
            reply_content = {
                "post_id": reply.find(class_="intro").get("id"),
                "ids_of_replied_posts": links,
                "username": reply.find(class_="name").get_text(),
                "date_posted": date,
                "image_links": self.extract_images(reply),
                "post_content": content,
            }
            replies[reply["id"]] = reply_content

        return replies

    def get_thread_contents(self):
        """Returns thread contents as a JSON"""
        original_post = self.extract_original_post()
        replies = self.extract_replies()

        thread_contents = {
            "thread number": self.threadNumber,
            "original post": original_post,
            "replies": replies,
        }

        return thread_contents

    def write_thread(self):
        """Opens a writeable text file, writes related headers and original post content on it and then closes file."""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.get_thread_contents(), f, indent=3, ensure_ascii=False)
