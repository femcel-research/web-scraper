import logging
from web_scraper.write_out import *
from bs4 import BeautifulSoup
from lxml import html

logger = logging.getLogger(__name__)


class SourceToContent:
    def __init__(self, board_name, source_json: dict, scan_time_str):
        logger.info(f"Accessing API data.")
        # Parse API JSON and make values (posts) accessible via indexing.
        self.posts: list = source_json["posts"]
        self.op_data: dict = self.posts[0]

        # Data values
        self.board_name: str = board_name
        self.thread_title: str = ""
        try:
            self.thread_title = self.op_data["sub"]  # thread subtitle
        except:
            semantic_url: str = self.op_data["semantic_url"]  # thread subtitle
            self.thread_title = semantic_url.replace("-", " ")
        self.thread_id: str = str(self.op_data["no"])  # thread number
        self.thread_url: str = (
            f"https://boards.4chan.org/{board_name}/thread/{self.thread_id}"
        )
        self.scrape_time = scan_time_str

        # Accessing and formatting post dates
        unix_timestamp: int = self.op_data["time"]
        date_posted: str = format_date(unix_to_datetime(unix_timestamp))
        latest_date: str = self.fetch_latest_date(self.posts)
        logger.debug("Successfully collected post dates from source JSON.")

        self.data: dict = {
            "board_name": self.board_name,
            "thread_title": self.thread_title,
            "thread_id": self.thread_id,
            "url": self.thread_url,
            "date_published": date_posted,
            "date_updated": latest_date,
            "date_scraped": self.scrape_time,
            "original_post": self.generate_post_data(self.op_data),
            "replies": self.generate_replies_data(self.posts),
        }

        logger.info(
            "Successfully extracted and collected all content data from source JSON."
        )

    def generate_post_data(self, post: dict):
        unix_timestamp: int = post["time"]
        date_posted: str = format_date(unix_to_datetime(unix_timestamp))
        post_id: str = str(post["no"])
        try:
            post_content_html: str = post["com"]
            post_content_html = post_content_html.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace('<span class="quote">', "\n")
            post_content = self.remove_comment_tags(post_content_html)
        except KeyError:
            post_content = ""
            logger.debug(f"Post ID {post_id} does not contain an comment. Post most likely only contains an image.")
        username: str = post["name"]

        # Replied to IDs
        if post["resto"] == 0:
            replied_to_ids: list = []
        else:
            replied_to_ids: list = [post["resto"]]
            

        # Img link recreation and finding tripcodes
        img_links: list[str] = []
        tripcode: str = ""
        try:
            img_extension: str = post["ext"]
            img_name: str = post["tim"]
            img_url: str = (
                f"http://i.4cdn.org/{self.board_name}/{img_name}{img_extension}"
            )
            img_links.append(img_url)
        except KeyError:
            logger.debug(f"Post {post_id} does not contain an image file.")

        try:
            tripcode = post["trip"]
        except KeyError:
            logger.debug(f"Post {post_id} does not contain an tripcode.")

        data = {
            "date_posted": date_posted,
            "post_id": post_id,
            "post_content": post_content,
            "img_links": img_links,  # List for consistency with replies
            "username": username,
            "tripcode": tripcode,
            "replied_to_ids": replied_to_ids,
        }
        logger.debug(
            f"Successfully extracted and collected all post data from Post {post_id}"
        )
        return data

    def generate_replies_data(self, all_posts: dict) -> dict:
        """Generates post data for thread replies
        Args:
            all_posts (dict): Dictionary containing all posts in the thread."""
        replies_data: dict = {}
        for post_idx in range(1, len(all_posts)):
            reply = self.posts[post_idx]
            reply_id: str = str(reply["no"])
            replies_data.update({f"reply_{reply_id}": self.generate_post_data(reply)})
        return replies_data

    def fetch_latest_date(self, all_posts: dict) -> str:
        """Given a list of replies, the latest one is returned.
        Args:
            list_of_replies (list[Post]): List of all replies within a given thread"""
        latest_date = datetime(1000, 1, 1, 0, 0, 0, 0)
        for post_idx in range(0, len(all_posts)):
            # Find post unix timestamp and convert to datetime obj
            post: dict = self.posts[post_idx]
            unix_timestamp: int = post["time"]
            post_datetime: datetime = unix_to_datetime(unix_timestamp)

            # if the reply has a later date then update latest_date
            if latest_date < post_datetime:
                latest_date = post_datetime

        # Format latest date into a str then return
        date: str = format_date(latest_date)
        return date

    def remove_comment_tags(self, comment: str) -> str:
        """Removes HTML tags from post comment
        Args:
            comment (str): String containing comment (body) of post."""
        # soup = BeautifulSoup(comment, "html.parser")
        # for data in soup(["style", "script"]):
        #     data.decompose()
        # return " ".join(soup.stripped_strings)
        return html.fromstring(comment).text_content()