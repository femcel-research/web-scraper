
# Imports
import logging

from bs4 import BeautifulSoup

from .exceptions import SoupError, TagNotFoundError, NoThreadLinkFoundError

logger = logging.getLogger(__name__)

class ArchiveScraper:
    """A tool to retrieve a list of (archive) URLs that can be iterated over.

    Given a URL to a page of a board on a 4chan archive, 
    a list of URLs is returned.

    Attributes:
        soup (BeautifulSoup): Made from the board archive.
        html_tag (str): HTML tag that each distinct post/post preview is 
            nested under on the archive site
        post_control (str): Word associated with the href for each post on the
            archive site
    """
    def __init__(self, html_content: bytes, html_tag: str, post_control: str):
        """Retrieves and returns a list of URLs.

        Args:
            html_content (bytes): The raw HTML content of the homepage.
            html_tag (str): The HTML tag that posts/post previews are nested under
            post_control (str): Word associated with the href for each post on the
            archive site

        Raises:
            SoupError: If a BeautifulSoup object can't be initialized.
        """
        self.html_tag: str = html_tag
        self.post_control: str = post_control
        try:
            self.soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
            logger.info("BeautifulSoup object initialized using html_content")
        except Exception as error:
            logger.error(
                f"Error initializing a BeautifulSoup object: {error}")
            raise SoupError(
                f"Error initializing a BeautifulSoup object: {error}")
        
    def archive_to_list(self) -> list[str]:
        """Extracts absolute thread URLs, retrieving from the specified tag.

        Under each instance of the tag that was specified during 
        initialization, a href associated with the word specified during 
        initialization is searched for and added to a list.

        Returns:
            list[str]: A list of absolute thread URLs from the archive page.
        
        Raises:
            TagNotFoundError: If no instances of the HTML tag are found.
            NoThreadLinkFoundError: If no href associated with the
                initialized word is found.
        """
        logger.info("Beginning the process to extract thread archive URLs")
        tag_elements = self.soup.find_all(self.html_tag)
        if not tag_elements:
            logger.error(
                f"Element with tag '{self.html_tag}' not found.")
            raise TagNotFoundError(
                f"Element with tag '{self.html_tag}' not found.")
        logger.info("Elements with specified tag found.")

        url_list = []
        for element in tag_elements:
            element_urls = element.find_all(
                'a', href=True, string=self.post_control)
            if element_urls:
                logger.info(
                    f"URLs with anchor text '{self.post_control}' found.")
                for url in element_urls: 
                    url_list.append(url['href'])
                    logger.info(f"Appended url {url['href']} to list")              
        if not url_list:
            logger.error(
                f"URLs with anchor text '{self.post_control}' not found.")
            raise NoThreadLinkFoundError(
                f"URLs with anchor text '{self.post_control}' not found.")
        
        logger.info("Successfully returning list of URLs")
        return url_list
