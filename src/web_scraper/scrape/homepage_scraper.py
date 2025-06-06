# Imports
import logging

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .exceptions import SoupError, ContainerNotFoundError, NoListItemsFoundError

logger = logging.getLogger(__name__)

class HomepageScraper:
    """A tool to retrieve a list of (homepage) URLs that can be iterated over.

    Given a URL to a chan-style homepage, in which internal links are
    stored under the "box right" class, a list of URLs (with the appropriate
    domain name appended to the front) is returned.

    Attributes:
        soup (BeautifulSoup): Made from the homepage.
        domain_param (str): The string that will be concatenated with 
            relative URLs.
        container_param (str): Class URLs are stored in.
    """
    def __init__(self, html_content: bytes, root_domain: str, container: str):
            """Retrieves and returns a list of URLs.

            Args:
                html_content (bytes): The raw HTML content of the homepage.
                url (str): URL prefix concatenated with relative URLs.
                container (str): Class URLs are stored in.

            Raises:
                SoupError: If a BeautifulSoup object can't be initialized.
            """
            self.domain_param: str = root_domain
            self.container_param: str = container
            try:
                self.soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
                logger.info("BeautifulSoup object initialized using html_content")
            except Exception as error:
                logger.error(
                    f"Error initializing a BeautifulSoup object: {error}")
                raise SoupError(
                    f"Error initializing a BeautifulSoup object: {error}")
    
    def homepage_to_list(self) -> list[str]:
        """Extracts absolute thread URLs from the specified container.

        Returns:
            list[str]: A list of absolute thread URLs from the homepage.

        Raises:
            ContainerNotFoundError: If the container element is not found.
            NoListItemsFoundError: If no list items found within container.
        """
        logger.info("Beginning the process to extract thread URLs")
        container = self.soup.find(class_=self.container_param)
        if container is None:
            logger.error(
                f"Container with class '{self.container_param}' not found.")
            raise ContainerNotFoundError(
                f"Container with class '{self.container_param}' not found.")
        logger.info("Container specified in parameter found")

        list_items = container.find_all("li")
        if not list_items:
            logger.error(
                f"No list items found within the container '{self.container_param}'.")
            raise NoListItemsFoundError(
                f"No list items found within the container '{self.container_param}'."
            )
        logger.info("List items found within the container")
        
        url_list = []
        for li_tag in list_items:
            anchor_tag = li_tag.find("a")
            if anchor_tag:
                # Get the value of "href" attribute; url info
                href = anchor_tag.get("href")
                if href:
                    # Ensure the URL is absolute
                    absolute_url = urljoin(self.domain_param, href)
                    url_list.append(absolute_url)
                    logger.info(f"Appended url {absolute_url} to list")
                else:
                    logger.warning(
                        f"Found <a> tag without 'href' in container '{self.container_param}'.")
            else:
                 logger.warning(
                     f"Found <li> tag without <a> in container '{self.container_param}'.")

        logger.info("Successfully returning list of URLs")
        return url_list