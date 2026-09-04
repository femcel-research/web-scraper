import glob
import json
import logging
import sys

from bs4 import BeautifulSoup
from pathlib import Path


from web_scraper.fourchan.utils.board_scraper import BoardScraper
from web_scraper.fourchan.utils.parse.Parser import Parser
from web_scraper.utils.datetime_helpers import *
from web_scraper.fourchan.utils import *
from basc_py4chan import *
import time

from web_scraper.utils.write_out import *

logger = logging.getLogger(__name__)

def fourchan_scrape(params_name: str, scan_time_str: str) -> None:
    """Scrapes and parses data from a specified website.
    Args:
        params_name (str): Name of website that corresponds to its respective params file
        scan_time_str (str): String containing the scan time
    """
    params: dict = params_retrieval(params_name)
    last_scrape: datetime = find_last_scrape_date(params, scan_time_str)

    scraper: BoardScraper = BoardScraper(params["board_name"])
    list_of_threads: list[Thread] = scraper.all_threads_to_list()

    for thread in list_of_threads:
        thread: Thread
        thread_id: str = str(thread.id)

        # Processes thread
        Parser(params, scan_time_str, last_scrape, thread, thread_id)
        # to not overload server
        time.sleep(1)  # wait 1s before looping again


def params_retrieval(params_name) -> dict:
    """
    Retrieves relevant parameters.
    """
    # Parameters
    params_file_list = glob.glob(f"./data/params/{params_name}*.json")
    params_file = params_file_list[0] if params_file_list else None
    
    if params_file is None:
        logger.critical(f"Parameters file name is not valid: {params_name}")
        logger.critical("Aborting")
        sys.exit(1)
    else:
        logger.debug(f"Parameters file name is valid: {params_name}")
        logger.debug("Choosing the first file containing the name")
    
    params_path = Path(params_file)
    params: dict
    try:
        with open(params_path, "r") as params_file:
            params = json.load(params_file)
        logger.info("Loaded parameters successfully")
    except FileNotFoundError:
        logger.critical("Parameters file not found with open")
        logger.critical("Aborting")
        sys.exit(1)
    except json.JSONDecodeError as error:
        logger.critical(f"Parameters file unable to be decoded: {error}")
        logger.critical("Aborting")
        sys.exit(1)
    except Exception as error:
        # Any other potential errors during file handling
        logger.critical(
            f"An unexpected error occurred while loading parameters: {error}"
        )
        logger.critical("Aborting")
        sys.exit(1)
    return params