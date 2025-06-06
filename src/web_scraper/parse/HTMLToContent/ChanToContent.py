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

    Attributes:
        self.data (dict): A dictionary of all data for a thread snapshot.

    TODO: Add tripcode collection functionality
    """

    def __init__(
            self, date_scraped: str,
            thread_soup: BeautifulSoup, snapshot_url: str, site_dir: str,
            op_class: str, reply_class: str, root_domain: str):
        """Given the HTML for a chan-style thread snapshot, data is collected.

        The ChanToContent object collects all data-to-be-used from the soup
        object on initialization, ready to be written out to a JSON.

        Args:
            scrape_time (str): Formatted time of scrape.
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

        self.date_scraped = date_scraped
        self.thread_soup = thread_soup
        self.snapshot_url = snapshot_url
        self.site_dir = site_dir  # Parameter
        self.op_class = op_class  # Parameter
        self.reply_class = reply_class  # Parameter
        self.root_domain = root_domain  # Parameter

        # Initialization: Extracting all data from the thread_soup
        self.logger.info("Beginning the process of extracting content data " \
            "from this thread snapshot's soup object")
        try:
            # Extracting the board name and thread title
            self.board_name: str = self.get_board_name_and_thread_title()\
                ["board"]
            self.thread_title: str = self.get_board_name_and_thread_title()\
                ["title"]
            
            # Extracting the thread ID
            self.thread_id: str = self.get_thread_id()

            # Extracting the date published (when the page was created) 
            # and date updated (when the page was most recently changed)
            self.date_published: str = self.get_date_published_and_updated()\
                ["date_published"]
            self.date_updated: str = self.get_date_published_and_updated()\
                ["date_updated"]
            
            # Extracting the original post Tag
            original_post_tag: Tag = self.get_original_post()

            # Extracting the list of reply post Tags
            reply_post_tag_list: list[Tag] = self.get_reply_posts()
            
            # Collecting the data from each post (OP and each reply post)
            self.all_post_data: dict = self.get_all_post_data(
                original_post_tag, reply_post_tag_list)
            
            # Final assignment of everything to tags in a dictionary
            self.data: dict = self.collect_all_data()
        except Exception as error:
            self.logger.error(f"Error when trying to initialize: {error}")
            raise ContentInitError(
                f"Error when trying to initialize: {error}") from error
        # End of initialization
        self.logger.info(
            "Successfully extracted and collected all content data from the "\
                f"snapshot of thread {self.thread_id}")
        
    def get_board_name_and_thread_title(self) -> dict:
        """Extracts a board name/title from the initialized soup object.
        
        The return dictionary values are strings.

        Returns:
            A dictionary with "board" and a "title" keys.

        Raises:
            BoardNameAndTitleNotFoundError: If a board name/title isn't found.
        """
        self.logger.debug("Searching for a board name/title")
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
            TagNotFoundError: If a thread ID cannot be found.
        """
        self.logger.debug("Searching for a thread ID")
        # Every chan-style site we've seen has an intro class, under
        # the op_class (parameter) in the HTML. If there is no "id" in
        # the intro class, then `None` is returned, and a different
        # method is used to search for the "id"
        try:
            thread_id = self.thread_soup.find(class_="intro").get("id")
        except:
                self.logger.error("Thread ID unable to be located")
                raise TagNotFoundError("Thread ID unable to be located")
        if thread_id is None:
            try:
                thread_id = self.thread_soup.find(class_="intro").find("a")\
                    .get("id").replace("post_no_", "")
                self.logger.debug(f"ID successfully found: {thread_id}")

                return thread_id
            except:
                self.logger.error("Thread ID unable to be located")
                raise TagNotFoundError("Thread ID unable to be located")
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
        self.logger.debug("Searching for publish and update dates")
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

        Raises:
            TagNotFoundError: If an OP can't be found with a parameter.
        """
        self.logger.debug("Searching for original post")
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

        Raises:
            TagNotFoundError: If replies can't be found with a parameter.
        """
        self.logger.debug("Searching for reply posts")
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

    def get_original_post_data(self, original_post: Tag) -> dict:
        """Extracts all necessary data from an original post.
        
        Collects the `date_posted`, `post_id`, `post_content`,
        `image_links`, `username`, `tripcode` (if available), and 
        `replied_to_ids` data from an original post, using the parameters
        from initialization. For further information on what each tag
        represents, check the documentation associated with this project.

        TODO: Add tripcode collection functionality
        TODO: If a tripcode isn't available, it is assigned an empty string.

        Arguments:
            original_post (Tag): Where the post data should originate from.

        Returns:
            A dictionary of the tags above and their corresponding data.

        Raises:
            DataArrangementError: When there is a problem with a post's data.
        """
        try:
            date_posted: str = self.get_post_date(original_post)
            try:
                post_id: str = self.get_post_id(original_post)
            except:
                # The OP ID should match the overall thread ID
                # so this is a sufficient backup (and behavior
                # that doesn't need to be replicated for reply posts)
                post_id: str = self.thread_id
            post_content: str = self.get_post_content(original_post)
            # Include the thread image as OP image (unlikely to cause
            # duplicates because the thread image has only been seen
            # beyond the scope of the original post tag)
            img_links: list[str] = self.get_thread_image_link
            img_links.append(self.get_post_image_links(original_post))
            username: str = self.get_post_username(original_post)
            replied_to_ids: list[str] = self.get_post_replied_to_ids(
                original_post)
            original_post_data = {
                "date_posted":
                    date_posted,
                "post_id": 
                    post_id,
                "post_content":
                    post_content,
                "img_links": 
                    img_links,
                "username":
                    username,
                # "tripcode":
                #     ,
                "replied_to_ids":
                    replied_to_ids}
            
            return original_post_data
        except:
            self.logger.error(f"Error in post data: {original_post}")
            raise DataArrangementError (
                f"Error in post data: {original_post}")

    def get_reply_post_data(self, reply_post: Tag) -> dict:
        """Extracts all necessary data from an individual reply post.
        
        Collects the `date_posted`, `post_id`, `post_content`,
        `image_links`, `username`, `tripcode` (if available), and 
        `replied_to_ids` data from a reply post, using the parameters
        from initialization. For further information on what each tag
        represents, check the documentation associated with this project.

        TODO: Add tripcode collection functionality
        TODO: If a tripcode isn't available, it is assigned an empty string.

        Arguments:
            reply_post (Tag): Where the post data should originate from.

        Returns:
            A dictionary of the tags above and their corresponding data.

        Raises:
            DataArrangementError: When there is a problem with a post's data.
        """
        try:
            date_posted: str = self.get_post_date(reply_post)
            post_id: str = self.get_post_id(reply_post)
            post_content: str = self.get_post_content(reply_post)
            img_links: list[str] = self.get_post_image_links(reply_post)
            username: str = self.get_post_username(reply_post)
            replied_to_ids: list[str] = self.get_post_replied_to_ids(
                reply_post)
            reply_post_data = {
                "date_posted":
                    date_posted,
                "post_id": 
                    post_id,
                "post_content":
                    post_content,
                "img_links": 
                    img_links,
                "username":
                    username,
                # "tripcode":
                #     ,
                "replied_to_ids":
                    replied_to_ids}
            
            return reply_post_data
        except:
            self.logger.error(f"Error in post data: {reply_post}")
            raise DataArrangementError (
                f"Error in post data: {reply_post}")

    def get_post_date(self, post_tag: Tag) -> str:
        """Extracts the date and time from a given post.
        
        The date and time is formatted according to the formatting standards
        used elsewhere throughout the project: `%Y-%m-%dT%H:%M:%S`

        Arguments:
            post_tag (Tag): The bs4 Tag corresponding to a post (OP/reply).

        Returns:
            The date and time from a post formatted as a string.

        Raises:
            TagNotFoundError: If replies can't be found with a parameter.
        """
        self.logger.debug("Searching for post date")
        try:
            date_posted: Tag = post_tag.find("time")
            if date_posted is None:
                self.logger.error("Post date found, but empty")
                raise TagNotFoundError("Post date found, but empty")
            else:
                date_string = date_posted["datetime"]
                # Converts post date to a datetime object
                date_datetime = datetime.strptime(
                    date_string, "%Y-%m-%dT%H:%M:%SZ")
                # Formats object to be more uniform
                date_formatted = date_datetime.strftime("%Y-%m-%dT%H:%M:%S")
                self.logger.debug(
                    f"Post date successfully found: {date_formatted}")
                
                return date_formatted
        except Exception as error:
            self.logger.error(f"Post date not found: {error}")
            raise TagNotFoundError (f"Post date not found: {error}")
        
    def get_post_id(self, post_tag: Tag) -> str:
        """Extracts the ID from a given post.
        
        Arguments:
            post_tag (Tag): The bs4 Tag corresponding to a post (OP/reply).

        Returns:
            The ID from a post as a string.

        Raises:
            TagNotFoundError: If an ID can't be found.    
        """
        self.logger.debug("Searching for post ID")
        try:
            # Get the attribute of the 'id' tag
            try: 
                post_id: str = post_tag.find(class_="intro").get("id")
                if post_id is None:
                    # Alternative structure seen for reply posts, specifically
                    post_id: str = post_tag.get("id").replace("reply_", "")
                    if post_id is None:
                        self.logger.error("Post ID found, but empty")
                        raise TagNotFoundError("Post ID found, but empty")
                    else:
                        
                        return post_id
            # If the 'id' tag doesn't exist, then catch the Exception
            except:
                # Alternative structure seen for reply posts, specifically
                post_id: str = post_tag.get("id").replace("reply_", "")
                if post_id is None:
                    self.logger.error("Post ID found, but empty")
                    raise TagNotFoundError("Post ID found, but empty")
                else:
                    
                    return post_id
            else:
                self.logger.debug(
                    f"Post ID successfully found: {post_id}")
                
                return post_id
        except Exception as error:
            self.logger.error(f"Post ID not found: {error}")
            raise TagNotFoundError (f"Post ID not found: {error}")
        
    def get_post_content(self, post_tag: Tag) -> str:
        """Extracts the content from a given post.

        The content of any given post is extracted from the post body.
        Line breaks are preserved, and weird formatting is preserved as well
        as possible.

        'Content' in this context refers to the content of the post, not the
        file type which contains all of the data from a particular snapshot
        of a thread.
        
        Arguments:
            post_tag (Tag): The bs4 Tag corresponding to a post (OP/reply).

        Returns:
            The content from a post as a formatted string.

        Raises:
            TagNotFoundError: If a post body can't be found.    
        """
        self.logger.debug("Searching for post content")
        try:
            post_body: Tag = post_tag.find(class_="body")
            if post_body is None:
                self.logger.error("Post content (body) found, but empty")
                raise TagNotFoundError("Post content (body) found, but empty")
            else:
                post_text: str = post_body.get_text('\n', True)
                self.logger.debug("Post content successfully found")

                return post_text
        except Exception as error:
            self.logger.error(f"Post content not found: {error}")
            raise TagNotFoundError (f"Post content not found: {error}")
        
    def get_post_image_links(self, post_tag: Tag) -> list[str]:
        """Extracts the image links from a given post.

        For each <image> tag in a given post, its source is retrieved
        and added to a list of image links. Depends on the class for
        the <image> tag being `post-image`.

        Utilizes the parameter `root_domain` to generate absolute URLs.

        A post with multiple image links in it has not been observed,
        but this implementation utilizes a list to account for any posts
        that may not have been observed before.

        Does not raise a TagNotFoundError because it is normal for a post to
        have no image attached to it.
        An empty list is returned if no image links are found.
        
        Arguments:
            post_tag (Tag): The bs4 Tag corresponding to a post (OP/reply).

        Returns:
            List of (absolute) image URLs from a post as a list of strings.

        Raises:
            Exception: A generic exception for unanticipated errors.
        """
        self.logger.debug("Searching for image links within post")
        image_links: list[str] = []
        try:
            image_tag: Tag
            for image_tag in post_tag.find_all("img", class_="post-image"):
                image_source: str = image_tag.get("src")
                if image_source:
                    image_links.append(f"{self.root_domain}{image_source}")
                    self.logger.debug(
                        "Image link within post successfully found: "
                        f"{self.root_domain}{image_source}")

            return image_links
        except Exception as error:
            self.logger.error(
                f"Unexpected error when collecting images: {error}")
            raise Exception(
                f"Unexpected error when collecting images: {error}")
        
    def get_thread_image_link(self) -> str:
        """Extracts the image link used to start a thread.
        
        Utilizes the parameter `root_domain` to generate absolute URLs.

        Depends on a thread ID having already been extracted.

        The thread image is stored outside of the original post tag,
        so this method should be used in conjunction with
        `get_post_image_links()` to gather all images that may be
        associated with the original post.

        Returns:
            An absolute image URL from the thread.

        Raises:
            TagNotFoundError: If a thread image can't be found. 
        """
        self.logger.debug("Searching for a thread image link")
        try:
            thread_tag: Tag = (
                # This remains consistent across all chan-style sites observed
                self.thread_soup.find("div", id=f"thread_{self.thread_id}"))
            # First image always appears to be the thread image
            image_source: str = thread_tag.find("img").get("src")
            if image_source is None:
                self.logger.error("Thread image link found, but empty")
                raise TagNotFoundError("Thread image link found, but empty")
            else:
                image_link: str = f"{self.root_domain}{image_source}"
                self.logger.debug("Thread image link successfully found")

                return image_link
        except Exception as error:
            self.logger.error(f"Thread image link not found: {error}")
            raise TagNotFoundError (f"Thread image link not found: {error}")
        
    def get_post_username(self, post_tag: Tag) -> str:
        """Extracts a username from a given post.
        
        Returns:
            A username as a string.

        Raises:
            TagNotFoundError: If a username cannot be found.
        """
        self.logger.debug("Searching for a post username")
        try:
            post_username: str = post_tag.find(class_="name").get_text()
            if not post_username:
                self.logger.error("Post username found, but empty")
                raise TagNotFoundError("Post username found, but empty")
            else: 
                formatted_post_username: str = post_username.strip().replace(
                    "\n", "")
                self.logger.debug("Post username successfully found")

                return formatted_post_username
        except Exception as error:
            self.logger.error(f"Post username not found: {error}")
            raise TagNotFoundError (f"Post username not found: {error}")

    def get_post_replied_to_ids(self, post_tag: Tag) -> list[str]:
        """Extracts a list of posts being replied to from a given post.

        Does not raise a TagNotFoundError because it is normal for a post to
        not be a reply to another post.
        An empty list is returned if there are no replied-to posts.
        
        Returns:
            A list of posts ID strings being replied to.

        Raises:
            Exception: A generic exception for unanticipated errors.
        """
        self.logger.debug("Searching for replied-to post IDs")
        try:
            post_body: Tag = post_tag.find(class_="body")
            links_to_other_posts: str
            links_to_other_posts = post_body.find_all(
                # Prevents external links from being added
                "a", attrs={"href": re.compile("^/")})
            post_links: list[str] = []
            if links_to_other_posts:
                self.logger.debug("Replied-to post IDs sucessfully found")
                link: Tag
                for link in links_to_other_posts:
                    post_links.append(link.text.strip().replace(">", ""))
            else:
                self.logger.debug("No replied-to post IDs found")

            return post_links
        except Exception as error:
            self.logger.error(
                f"Unexpected error when extracting replied-to IDs: {error}")
            raise Exception(
                f"Unexpected error when extracting replied-to IDs: {error}")
    
    def get_all_post_data(self, op: Tag, replies: list[Tag]) -> dict:
        """Collects a formatted dictionary of all data from every post.
        
        The original post and every reply is contained within the returned
        dictionary, along with each post's post date, post ID, post
        content, image links, username, and replied-to posts.

        Arguments:
            op (Tag): The original_post Tag.
            replies (list[Tag]): The list of reply_post Tags.

        Returns:
            A dictionary of every post (and its data) from the thread.

        Raises:
            DataArrangementError: When putting it all together goes wrong.
        """
        self.logger.debug("Collecting data from every post in the thread")
        try:
            all_post_data: dict = {}

            all_post_data["original_post"] = self.get_original_post_data(op)

            reply: Tag
            for reply in replies:
                all_post_data[f"reply_{self.get_post_id(reply)}"] = (
                    self.get_reply_post_data(reply))
            self.logger.debug("Data from every post successfully collected")

            return all_post_data
        except Exception as error:
            self.logger.error("Error while collecting all post data")
            raise DataArrangementError("Error while collecting all post data")
    
    def collect_all_data(self) -> dict:
        """The final call during initialization; collects all data to dict.
        
        Depends on every other initialization process being complete.

        Returns:
            The final dictionary of all data, ready to be written to a JSON.
        
        Raises:
            DataArrangementError: When something goes wrong?
        """
        self.logger.debug(
            "Collecting all data from thread snapshot into a dictionary")
        try:
            all_snapshot_data: dict = {
                "board_name":
                    self.board_name,
                "thread_title":
                    self.thread_title,
                "thread_id":
                    self.thread_id,
                "url":
                    self.snapshot_url,
                "date_published":
                    self.date_published,
                "date_updated":
                    self.date_updated,
                "date_scraped":
                    self.date_scraped,
                "posts":
                    self.all_post_data}
            
            return all_snapshot_data
        except:
            self.logger.error("Error during final collection of thread data")
            raise DataArrangementError(
                "Error during final collection of thread data")