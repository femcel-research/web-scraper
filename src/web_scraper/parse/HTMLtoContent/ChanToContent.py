# Imports
import json
import logging
import os
import re

from bs4 import BeautifulSoup, Tag
from htmldate import find_date  # Used for finding date published and date updated
from datetime import datetime

from .exceptions import *

class ChanToContent:
    """Takes HTML from a chan-style thread and formats it (for a JSON).
    
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
    """

    def __init__(
            self, scrape_time: datetime,
            thread_soup: BeautifulSoup, snapshot_url: str, site_dir: str,
            op_class: str, reply_class: str, root_domain: str,
            post_date_location: str):
        """Given the HTML for a chan-style thread snapshot, data is collected.

        The ChanToContent object collects all data-to-be-used from the soup
        object on initialization, ready to be written out to a JSON.

        Args:
            scrape_time (datetime): Time of scrape.
            thread_soup (BeautifulSoup): HTML from a thread in a soup object.
            snapshot_url (str): NOT a parameter, URL of the thread snapshot.
            site_dir (str): Directory for content files.
            op_class (str): Name of class for original posts.
            reply_class (str): Name of class for post replies.
            root_domain (str): Used as a prefix in image URLs.
            post_date_location (str): Class/label string for date and time.

        Raises: 
            ContentInitError: If an error occurs during initialization.
        """
        self.logger = logging.getLogger(__name__)

        # TODO: Maybe scrape_time should be a pre-formatted string?
        self.scrape_time = scrape_time
        self.thread_soup = thread_soup
        self.snapshot_url = snapshot_url
        self.site_dir = site_dir  # Parameter
        self.op_class = op_class  # Parameter
        self.reply_class = reply_class  # Parameter
        self.root_domain = root_domain  # Parameter
        self.post_date_location = post_date_location  # Parameter

        # Initialization: Extracting all data from the thread_soup
        self.logger.info("Beginning the process of extracting content data " \
            "from this thread snapshot's soup object")
        # Extracting the board name and thread title
        try:
            self.board_name: str = self.get_board_name_and_thread_title()\
                ["board"]
            self.thread_title: str = self.get_board_name_and_thread_title()\
                ["title"]
        except Exception as error:
            self.init_error_log_raise(error)
        # Extracting the thread ID
        try:
            self.thread_id: str = self.get_thread_id()
        except Exception as error:
            self.init_error_log_raise(error)
        # Extracting the date published (when the page was created) 
        # and date updated (when the page was most recently changed)
        try:
            self.date_published: str = self.get_date_published_and_updated()\
                ["date_published"]
            self.date_updated: str = self.get_date_published_and_updated()\
                ["date_updated"]
        except Exception as error:
            self.init_error_log_raise(error)
        # Extracting the original post Tag
        try:
            self.original_post_tag: Tag = self.get_original_post()
        except Exception as error:
            self.init_error_log_raise(error)
        # Extracting the list of reply post Tags
        try:
            self.reply_post_tag_list: list[Tag] = self.get_reply_posts()
        except Exception as error:
            self.init_error_log_raise(error)
        # End of initialization
        self.logger.info(
            "Successfully extracted and collected all content data from the "\
                f"snapshot of thread {self.thread_id}")
    
    def init_error_log_raise(self, error: Exception):
        """Posts the passed exception in log as an error, and raises it.
        
        Used to reduce repetition in __init__().

        Raises:
            ContentInitError: When an error occurs during initializaton.
        """
        self.logger.error(f"Error when trying to initialize: {error}")
        raise ContentInitError(
            f"Error when trying to initialize: {error}") from error

    def get_board_name_and_thread_title(self) -> dict:
        """Extracts a board name/title from the initialized soup object.
        
        The return dictionary values are strings.

        Returns:
            A dictionary with "board" and a "title" keys.

        Raises:
            BoardNameAndTitleNotFoundError: If a board name/title isn't found.
        """
        self.logger.debug(f"Searching for a board name/title")
        # Search for a <title> tag in the HTML and extract
        try:
            page_title: str = self.thread_soup.title.string
        except:
            self.logger.error("Page title unable to be located")
            raise BoardNameAndTitleNotFoundError(
                f"Page title unable to be located")
        # If it's empty, then it's unsupported, otherwise parse it
        if page_title is None:
            self.logger.error("Page title unable to be located")
            raise BoardNameAndTitleNotFoundError(
                f"Page title unable to be located")
        else:
            if "-" in page_title:
                # Splits board name and thread title...
                # The format is ubiquitously `/board/ - Title`
                board_and_title = re.split("[-]", page_title)
                for x in range(len(board_and_title)):
                    board_and_title[x] = board_and_title[x].strip()
                board = board_and_title[0]
                title = board_and_title[1]
                self.logger.debug("Board and title successfully found:"\
                    f"{board}, {title}")
                
                return {"board": board, "title": title}
            else:
                # Unsupported format
                self.logger.error("Board name/title unable to be parsed")
                raise BoardNameAndTitleUnsupportedError(
                    "Board name/title unable to be parsed")

    def get_thread_id(self) -> str:
        """Extracts a thread ID from the initialized soup object.
        
        Returns:
            The thread ID as a string.
        
        Raises:
            ThreadIDNotFoundError: If a thread ID cannot be found.
        """
        self.logger.debug(f"Searching for a thread ID")
        # Every chan-style site we've seen has an intro class, under
        # the op_class (parameter) in the HTML. If there is no "id" in
        # the intro class, then `None` is returned, and a different
        # method is used to search for the "id"
        try:
            thread_id = self.thread_soup.find(class_="intro").get("id")
        except:
                self.logger.error("Thread ID unable to be located")
                raise ThreadIDNotFoundError("Thread ID unable to be located")
        if thread_id is None:
            try:
                thread_id = self.thread_soup.find(class_="intro").find("a")\
                    .get("id").replace("post_no_", "")
                self.logger.debug(f"ID successfully found: {thread_id}")

                return thread_id
            except:
                self.logger.error("Thread ID unable to be located")
                raise ThreadIDNotFoundError("Thread ID unable to be located")
        else:
            self.logger.debug(f"ID successfully found: {thread_id}")

            return thread_id
        
    def get_date_published_and_updated(self) -> dict:
        """Extracts date published and date updated from the HTML.

        The return dictionary values are strings.
        
        Returns:
            A dictionary with "date_published" and a "date_updated" keys.

        Raises:
            BoardNameAndTitleNotFoundError: If a board name/title isn't found.
        """
        self.logger.debug(f"Searching for publish and update dates")
        html = str(self.thread_soup)  # Retrieves HTML from soup object
        # Uses htmldate lib to find original and update dates
        date_published = find_date(
            html,
            extensive_search=True,
            original_date=True,
            outputformat="%Y-%m-%dT%H:%M:%S",
        )
        if date_published is None:
            self.logger.error("Date published not found.")
            raise DateNotFoundError("Date published not found.")
        date_updated = find_date(
            html,
            extensive_search=False,
            original_date=False,
            outputformat="%Y-%m-%dT%H:%M:%S",
        )
        if date_updated is None:
            self.logger.error("Date updated not found.")
            raise DateNotFoundError("Date updated not found.")
        self.logger.debug("Date published and date updated successfully "\
            f"found: {date_published}, {date_updated}")
        
        return {"date_published": date_published, "date_updated": date_updated}
    
    def get_original_post(self) -> Tag:
        """Extracts the original post from the HTML.

        Utilizes the parameter `op_class` to find the original post.

        Returns:
            The original post as a Tag (from the bs4 lib).

        Raises
            TagNotFoundError: If an OP can't be found with a parameter.
        """
        self.logger.debug(f"Searching for original post")
        try:
            original_post: Tag = self.thread_soup.find(class_=self.op_class)
            if original_post is None:
                self.logger.error("Original post found, but empty")
                raise TagNotFoundError("Original post found, but empty")
            else:
                self.logger.debug("Original post successfully found")

                return original_post
        except Exception as error:
            self.logger.error(f"Original post not found: {error}")
            raise TagNotFoundError (f"Original post not found: {error}")


    def get_reply_posts(self) -> list[Tag]: 
        """Extracts the reply posts from the HTML.

        Utilizes the parameter `reply_class` to find the reply posts.
        If there are no replies, an empty list is returned.

        Returns:
            The reply posts as a list of Tags (from the bs4 lib).

        Raises
            TagNotFoundError: If replies can't be found with a parameter.
        """
        self.logger.debug(f"Searching for reply posts")
        try:
            reply_posts: list[Tag] = self.thread_soup.find_all(
                class_=self.reply_class)
            if reply_posts is None:
                self.logger.debug("No reply post(s) found")
            else:
                self.logger.debug(
                    f"Reply post(s) successfully found: {len(reply_posts)}")

                return reply_posts
        except Exception as error:
            self.logger.error(f"Reply post(s) not found: {error}")
            raise TagNotFoundError (f"Reply post(s) not found: {error}")
        pass

    # def get_original_post_data(self) -> dict:
    #     """Extracts all necessary data from an original post.
        
    #     Collects the `date_posted`, `post_id`, `post_content`,
    #     `image_links`, `username`, `tripcode` (if available), and 
    #     `replied_to_ids` data from an original post, using the parameters
    #     from initialization. For further information on what each tag
    #     represents, check the documentation associated with this project.

    #     If a tripcode isn't available, it is assigned an empty string.

    #     Returns:
    #         A dictionary of the tags above and their corresponding data.
    #     """
    #     try:
    #         date_posted: str = 
    #     original_post_data = {
    #         "date_posted":
    #             ,
    #         "post_id": 
    #             ,
    #         "post_content":
    #             ,
    #         "image_links": 
    #             ,
    #         "username":
    #             ,
    #         "tripcode":
    #             ,
    #         "replied_to_ids":

    #     }
    #     pass

    # def get_reply_post_data(self) -> dict:
    #     """Extracts all necessary data from a reply post.
        
    #     Collects the `date_posted`, `post_id`, `post_content`,
    #     `image_links`, `username`, `tripcode` (if available), and 
    #     `replied_to_ids` data from a reply post, using the parameters
    #     from initialization. For further information on what each tag
    #     represents, check the documentation associated with this project.

    #     If a tripcode isn't available, it is assigned an empty string.

    #     Returns:
    #         A dictionary of the tags above and their corresponding data.
    #     """
    #     reply_post_data = {
    #         "date_posted":
    #             ,
    #         "post_id": 
    #             ,
    #         "post_content":
    #             ,
    #         "image_links": 
    #             ,
    #         "username":
    #             ,
    #         "tripcode":
    #             ,
    #         "replied_to_ids":
            
    #     }
    #     pass

    def get_post_date(self, post_tag: Tag) -> str:
        """Extracts the date and time from a given post.
        
        The date and time is formatted according to the formatting standards
        used elsewhere throughout the project: `%Y-%m-%dT%H:%M:%S`

        Utilizes the `post_date_location` parameter.

        Arguments:
            post_tag (Tag): The bs4 Tag corresponding to a post (OP/reply).

        Returns:
            The date and time from a post formatted as a string.

        Raises
            TagNotFoundError: If replies can't be found with a parameter.
        """
        self.logger.debug(f"Searching for post date")
        try:
            date_posted: Tag = post_tag.find(self.post_date_location)
            if date_posted is None:
                self.logger.error("Post date found, but empty")
                raise TagNotFoundError("Post date found, but empty")
            else:
                date_string = date_posted["datetime"]
                # Converts post date to a datetime object
                date_datetime = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
                # Formats object to be more uniform
                date_formatted = date_datetime.strftime("%Y-%m-%dT%H:%M:%S")
                self.logger.debug(
                    f"Post date successfully found: {date_formatted}")
                
                return date_formatted
        except Exception as error:
            self.logger.error(f"Post date not found: {error}")
            raise TagNotFoundError (f"Post date not found: {error}")
    
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

    # def extract_text(self, post):
    #     """Extracts text from a given post and returns it as a string."""
    #     return post.get_text() 

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
    
    # def get_thread_contents(
    #         self, thread_number, original_post, post_replies, 
    #         url, post_date_location):
    #     """Returns thread contents as a JSON"""
    #     op = self.extract_original_post(
    #         original_post, url, post_date_location, thread_number)
    #     replies = self.extract_replies(post_replies, url, post_date_location)

    #     thread_contents = {
    #         "thread_number": 
    #             thread_number,
    #         "original_post": 
    #             op,
    #         "replies": 
    #             replies,
    #     }

    #     return thread_contents
