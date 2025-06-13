import datetime
import logging
import re
import time
import bs4
import basc_py4chan
from basc_py4chan import *
from write_out import *

logger = logging.getLogger(__name__)


class BoardToContent:
    def __init__(self, site_dir_path: str, thread: Thread, scrape_time: str):
        """Scrapes from a specific 4chan board"""
        self.thread: Thread = thread
        self.scrape_time: str = scrape_time
        self.site_dir_path: str = site_dir_path
        thread_id: str = str(self.thread.id)

        # Pathing:
        thread_dir: str = os.path.join(self.site_dir_path, thread_id)
        thread_snapshot_path: str = os.path.join(thread_dir, self.scrape_time)
        os.makedirs(thread_snapshot_path, exist_ok=True)

        # Data:
        board_name = str(self.thread._board)
        board_name = re.sub('[<>]', '', board_name)
        list_of_posts: list = self.thread.all_posts
        original_post: Post = self.fetch_original_post(list_of_posts)
        list_of_replies: list[Post] = self.fetch_replies(list_of_posts)
        latest_date: str = self.fetch_latest_date(list_of_replies)
        post_date: str = self.format_date(original_post.datetime)

        self.data: dict = {
            "board_name": board_name.replace("Board ", "").strip(),
            "thread_title": str(self.thread.topic.subject),
            "thread_id": thread_id,
            "url": self.thread.url,
            "date_published": post_date,
            "date_updated": latest_date,
            "date_scraped": self.scrape_time,
            "original_post": self.generate_post_data(original_post),
            "replies": self.generate_replies_data(list_of_replies),
        }

    def fetch_original_post(self, list_of_posts: list[Post]) -> Post:
        """Given a list of posts, the original post is retrieved.
        Args:
            list_of_posts (list[Post]): List of all posts within a given thread"""
        for post in list_of_posts:
            post: Post
            if post.is_op:
                return post

    def fetch_replies(self, list_of_posts: list[Post]) -> list[Post]:
        """Given a list of posts, only the replies to the original post are retrieved.
        Args:
            list_of_posts (list[Post]): List of all posts within a given thread"""
        replies: list[Post] = []
        for post in list_of_posts:
            post: Post
            if not post.is_op:  # adds all posts except OP
                replies.append(post)
        return replies

    def fetch_latest_date(self, list_of_replies: list[Post]) -> str:
        """Given a list of replies, the latest one is returned.
        Args:
            list_of_replies (list[Post]): List of all replies within a given thread"""
        latest_date = datetime(1000, 1, 1, 0, 0, 0, 0)
        for reply in list_of_replies:
            reply: Post
            if (
                latest_date < reply.datetime
            ):  # if the reply has a later date then update latest_date
                latest_date = reply.datetime
        date: str = self.format_date(latest_date)
        return date

    def generate_post_data(self, post: Post) -> dict:
        """Generates data from a post
        Args:
           post(Post): A post from a thread"""
        date_posted = self.format_date(post.datetime)
        post_id: str = str(post.post_id)
        post_content: str = post.text_comment
        replied_to_ids = self.gather_replied_to_ids(post_content)
        img_links: list[str] = self.gather_image_url(post) #4chan supports only one file per post
        username = post.name
        post_data = {
            "date_posted": date_posted,
            "post_id": post_id,
            "post_content": post_content,
            "img_links": img_links,
            "username": username,
            "replied_to_ids": replied_to_ids,
        }
        return post_data

    def generate_replies_data(self, post_replies: list[Post]) -> dict:
        """Generates data for each reply and returns it in a dictionary.
        Args:
            post_replies(list[Post]): List of all replies within thread"""
        replies: dict = {}
        for reply in post_replies:
            reply: Post
            replies[f"reply_{reply.number}"] = self.generate_post_data(reply)
        return replies

    def gather_replied_to_ids(self, post_content:str) -> list[int]:
        """Gathers IDs of all replies to a specific post.
        Args:
            post_content: Text content of a post."""
        replied_to_ids: list[int] = []
        words = post_content.split()
        for word in words:
            word: str
            if ">>" in word:
                candidate_id: str = word.replace(">>", "")
                if candidate_id.isdigit():
                    replied_to_ids.append(candidate_id)
        return replied_to_ids

    def gather_image_url(self, post: Post) -> list[str]:
        """Gathers file urls from a list of files.
        Args:
            files (list[File]): List of files from post"""
        post: Post
        if not post.has_file:
            return []
        else:
            file_urls: list[str] = []
            image: str = post.file.file_url #It looks like 4chan limits posters to adding one image
            file_urls.append(image)
            return file_urls

    def format_date(self, date) -> str:
        """Formats datetime object to %Y-%m-%dT%H:%M:%S
        Args:
            date (datetime): Date to be formatted"""
        formatted_date: str = datetime.strftime(date, "%Y-%m-%dT%H:%M:%S")
        return formatted_date
