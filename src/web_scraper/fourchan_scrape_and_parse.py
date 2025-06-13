# Imports
import glob
import json
import logging
import os
import sys
import time

from bs4 import BeautifulSoup
from pathlib import Path

from basc_py4chan import *

from fetch.fetcher import fetch_fourchan_json_content
from scrape.board_scraper import BoardScraper
from parse.MasterTextGenerator import MasterTextGenerator
from parse.HTMLToContent.BoardToContent import BoardToContent
from parse.MasterContentGenerator import MasterContentGenerator
from parse.MasterMetaGenerator import MasterMetaGenerator
from parse.SnapshotMetaGenerator import SnapshotMetaGenerator
from write_out import *

from write_out import *

logger = logging.getLogger(__name__)


def fourchan_scrape(params_name: str, scan_time_str: str) -> None:
    """Scrapes and parses data from a specified website.
    Args:
        params_name (str): Name of website that corresponds to its respective params file
        scan_time_str (str): String containing the scan time
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

    scraper: BoardScraper = BoardScraper(params["board_name"])
    list_of_threads: list[Thread] = scraper.threads_to_list()

    for thread in list_of_threads:
        thread: Thread
        thread_id: int = thread.id

        # Pathing:
        thread_dir: str = os.path.join(f"./data/{params["site_name"]}", str(thread_id))
        thread_snapshot_path: str = os.path.join(thread_dir, scan_time_str)
        os.makedirs(thread_snapshot_path, exist_ok=True)

        content_file_path: str = os.path.join(
            thread_snapshot_path, f"content_{thread_id}.json"
        )

        # Saves API data as dict:
        api_data: dict = fetch_fourchan_json_content(thread._api_url)
        snapshot_dict_to_json(api_data, scan_time_str, thread_id, "source", f"./data/{params["site_name"]}",)

        content_parser: BoardToContent = BoardToContent(
            params["site_dir"], thread, scan_time_str
        )

        # Content JSON creation:
        snapshot_dict_to_json(
            content_parser.data,
            scan_time_str,
            thread_id,
            "content",
            f"./data/{params["site_name"]}",
        )
        # TODO: Using the f-string for the data directory instead of
        # params["site_dir"] for now for testing

        # Snapshot meta creation:
        snapshot_meta_generator: SnapshotMetaGenerator = SnapshotMetaGenerator(
            content_file_path
        )
        snapshot_meta_generator.meta_dump()

        # Master content creation:
        candidate_content_files = os.path.join(thread_dir, "**", "content_*.json")
        list_of_snapshot_contents: list[str] = list(
            glob.glob(candidate_content_files, recursive=True)
        )
        master_content_generator: MasterContentGenerator = MasterContentGenerator(
            list_of_snapshot_contents,
        )
        master_content_generator.content_dump()

        # Master text creation:
        master_text_generator: MasterTextGenerator = MasterTextGenerator(
            os.path.join(
                thread_dir, f"master_version_{content_parser.data["thread_id"]}.json"
            ),
            params["site_dir"],
        )
        master_text_generator.write_text()

        # Master meta creation:
        candidate_meta_files = os.path.join(thread_dir, "**", "meta_*.json")
        list_of_snapshot_metas: list[str] = list(
            glob.glob(candidate_meta_files, recursive=True)
        )
        master_meta_generator: MasterMetaGenerator = MasterMetaGenerator(
            list_of_snapshot_metas
        )
        master_meta_generator.master_meta_dump()

        # to not overload server
        time.sleep(1)  # wait 1s before looping again
