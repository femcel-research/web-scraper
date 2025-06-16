# Imports
import logging

from urllib.parse import urljoin

from bs4 import BeautifulSoup
import bs4
import basc_py4chan
from basc_py4chan import *
from write_out import *

from .exceptions import SoupError, ContainerNotFoundError, NoListItemsFoundError

logger = logging.getLogger(__name__)


class BoardScraper:
    """A tool to retrieve a list of threads that can be iterated over.

    Given a 4chan board name, a list of threads on the board is returned.
    """

    def __init__(self, board_name):
        """Scrapes from a specific 4chan board"""
        self.board: Board = basc_py4chan.Board(board_name, True)

    def all_threads_to_list(self) -> list[Thread]:
        """Extracts threads from the specified board.

        Returns:
            list[Thread]: A list of thread objects from the board.
        """
        logger.info("Beginning the process to extract threads from board")
        try:
            list_of_threads: list[Thread] = self.board.get_all_threads(expand=True)

        except Exception as error:
            logger.error(f"Error retrieving threads: {error}")
            raise SoupError(f"Error retrieving threads: {error}")
        logger.info("Extraction complete!")
        return list_of_threads

    def page_threads_to_list(self, page_number: int) -> list[Thread]:
        """Extracts threads from the specific page on a board.

        Args:
            page_number (int): 4Chan page number

        Returns:
            list[Thread]: A list of thread objects from the board.
        """
        logger.info("Beginning the process to extract threads from board")
        try:
            list_of_threads: list[Thread] = self.board.get_threads(page=page_number)

        except Exception as error:
            logger.error(f"Error retrieving threads: {error}")
            raise SoupError(f"Error retrieving threads: {error}")
        logger.info("Extraction complete!")
        return list_of_threads
