# Imports
import logging

import random
import time
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import bs4
import basc_py4chan
from basc_py4chan import *
from write_out import *
from web_scraper.fetch.fetcher import *

from .exceptions import SoupError, ContainerNotFoundError, NoListItemsFoundError

logger = logging.getLogger(__name__)


class CatalogScraper:
    """A tool to retrieve a list of threads that can be iterated over.

    Given a site, a list of threads on the board is returned.
    """

    def __init__(self, html_content: bytes, root_domain: str, board_list: str):
        """Scrapes from the catalog of each board"""
        self.domain_param: str = root_domain
        self.board_list_container: str = board_list
        try:
            self.soup: BeautifulSoup = BeautifulSoup(
                html_content, "html.parser")
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
        container = self.soup.find(class_=self.board_list_container)
        if container is None:
            logger.error(
                f"Container with class '{self.board_list_container}' not found.")
            raise ContainerNotFoundError(
                f"Container with class '{self.board_list_container}' not found.")
        logger.info("Container specified in parameter found")

        board_links = container.find_all("a")
        if not board_links:
            logger.error(
                f"No list items found within the container '{self.board_list_container}'.")
            raise NoListItemsFoundError(
                f"No list items found within the container '{self.board_list_container}'."
            )
        logger.info("List items found within the container")

        base_url: str = self.domain_param
        url_list: list[str] = []
        for board in board_links:
            board: str = board.get_text()
            catalog = f"{self.domain_param}/{board}/catalog"
            catalogue_content = fetch_html_content(catalog)
            if catalogue_content:
                self.soup = BeautifulSoup(catalogue_content, "html.parser")
                # link extraction
                links = self.extract_links(self.soup, base_url)
                for link in links:
                    if "/thread/" in link:  # only get links w/ "/thread/"
                        url_list.add(link)

                page_number += 1
                # to not overload server
                # Delay between 10 and 30 seconds
                delay_seconds = random.uniform(1, 2)
                time.sleep(delay_seconds)

        logger.info("Successfully returning list of URLs")
        return url_list

    def extract_links(self, soup, base_url: str) -> list[str]:
        """
        Extracts all links from a BeautifulSoup object.
        """
        links = []
        for a_tag in soup.find_all("a"):
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
