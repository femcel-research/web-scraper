# Imports
import logging
import random
import time

from bs4 import BeautifulSoup

from .exceptions import SoupError, TagNotFoundError, NoThreadLinkFoundError
from web_scraper.fetch.fetcher import *

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
            logger.error(f"Error initializing a BeautifulSoup object: {error}")
            raise SoupError(f"Error initializing a BeautifulSoup object: {error}")

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
            logger.error(f"Element with tag '{self.html_tag}' not found.")
            raise TagNotFoundError(f"Element with tag '{self.html_tag}' not found.")
        logger.info("Elements with specified tag found.")

        url_list = []
        for element in tag_elements:
            element_urls = element.find_all("a", href=True, string=self.post_control)
            if element_urls:
                logger.info(f"URLs with anchor text '{self.post_control}' found.")
                for url in element_urls:
                    url_list.append(url["href"])
                    logger.info(f"Appended url {url['href']} to list")
        if not url_list:
            logger.error(f"URLs with anchor text '{self.post_control}' not found.")
            raise NoThreadLinkFoundError(
                f"URLs with anchor text '{self.post_control}' not found."
            )

        logger.info("Successfully returning list of URLs")
        return url_list

    # # From old scraper implementation, checking to see if this works with params
    def extract_links(self, base_url: str) -> list[str]:
        """
        Extracts all links from a BeautifulSoup object.
        """
        links = []
        for a_tag in self.soup.find_all("a"):
            href = a_tag.get("href")
            if href:
                # Converts relative URLs to absolute URLs
                if href.startswith("/"):
                    link = base_url + href
                # handles absolute URLs
                elif href.startswith("http"):
                    link = href
                links.append(link)
        return links

    def crawl_site_for_links(
        self, base_url: str, start_page=1, max_page=1
    ) -> list[str]:
        """
        Crawls the archive site, starting from the specified page up until a max page number, and returns a list of all extracted links.

        Args:
            start_page (int, optional): The page number to start from, defaults to 1.

        Returns:
            list: A list of all unique URLs found on the archive pages. Returns an empty list on error.
        """
        page_number = start_page
        all_links = set()  # use a set to store unique links
        crawled_count = 0

        # TODO: can make this into a while loop that continues until no content exists.
        for page_number in range(start_page, max_page + 1):
            # construct the URL for the current page.
            if page_number == 1:
                page_url = base_url
            else:
                page_url = f"{base_url}page/{page_number}/"

            logger.info(f"Crawling page: {page_url}")
            content = fetch_html_content(page_url)
            if content:
                crawled_count += 1
                self.soup = BeautifulSoup(content, "html.parser")

                # link extraction
                links = self.extract_links(base_url)
                for link in links:
                    if "/thread/" in link:  # only get links w/ "/thread/"
                        all_links.add(link)

                # to not overload server
                delay_seconds = random.uniform(60, 90) # Delay between 30 and 60 seconds
                time.sleep(delay_seconds) 

                page_number += 1
            else:
                logger.warning(
                    f"Failed to retrieve content from {page_url}.  Assuming this is the last page. Stopping."
                )
                break  # dont crawl if page doesn't load

        logger.debug(f"Crawling complete.  Crawled {crawled_count} pages.")
        # log the total number of unique links
        logger.debug(f"Found {len(all_links)} unique links.")
        return list(all_links)  # return the set of links as a list.
