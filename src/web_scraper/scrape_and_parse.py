# Imports
import argparse
import glob
import json
import logging
import os
import sys
import time

from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

from fetch import fetch_html_content
from scrape import ArchiveScraper
from scrape import HomepageScraper
from parse import MasterTextGenerator
from parse.HTMLToContent import ChanToContent
from parse.HTMLToContent.ArchiveToContent import ArchiveToContent
from parse.MasterContentGenerator import MasterContentGenerator
from parse.MasterMetaGenerator import MasterMetaGenerator
from parse.SnapshotMetaGenerator import SnapshotMetaGenerator

from write_out import *

logger = logging.getLogger(__name__)


def scrape_all(scan_time_str: str) -> None:
    """Scrapes and reparses data for all sites within the data params subfolder
    Args:
        scan_time_str (str): String containing the scan time"""
    params_directory = f"./data/params"
    # Iterates through all param files and scrapes and reparses its respective site
    for params_file_name in os.listdir(params_directory):
        params_name = params_file_name.replace("_params.json", "")
        if "archive" in params_name or "4chan_" in params_name: #excludes archives and 4chan from scrape all
            continue
        else:
            scrape(params_name, scan_time_str)


def scrape(params_name: str, scan_time_str: str) -> None:
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

    # Bool determining ehther or not website is an archive
    archive: bool = False
    if "archive" in params["site_name"]: #TODO: in future maybe add an archive bool key to site param files and read from that
        archive = True

    homepage: bytes = fetch_html_content(params["hp_url"])

    url_list: list[str] = []

    if archive:
        # archive_scraper: ArchiveScraper = ArchiveScraper(
        #     homepage, params["domain"], params["container"]
        # )
        # url_list: list[str] = archive_scraper.crawl_site_for_links(
        #     params["hp_url"], 1, 1
        # )
        logging.warning("Archive site detected; WIP; skipping")
        pass  # Archive is still being worked on
    else:
        scraper: HomepageScraper = HomepageScraper(
            homepage, params["domain"], params["container"]
        )
        url_list = scraper.homepage_to_list()

    for url in url_list:
        soup = BeautifulSoup(fetch_html_content(url), features="html.parser")
        if archive:
            # content_parser: ArchiveToContent = ArchiveToContent(
            #     scan_time_str,
            #     soup,
            #     url,
            #     params["op_class"],
            #     params["reply_class"],
            #     params["id_class"],
            #     params["root_domain"],
            # )
            pass
        else:
            content_parser: ChanToContent = ChanToContent(
                scan_time_str,
                soup,
                url,
                params["op_class"],
                params["reply_class"],
                params["root_domain"],
            )

        # Pathing:
        thread_dir: str = os.path.join(
            f"./data/{params["site_name"]}", content_parser.data["thread_id"]
        )
        thread_snapshot_path: str = os.path.join(thread_dir, scan_time_str)
        os.makedirs(thread_snapshot_path, exist_ok=True)

        content_file_path: str = os.path.join(
            thread_snapshot_path, f"content_{content_parser.data["thread_id"]}.json"
        )
        html_file_path: str = os.path.join(
            thread_snapshot_path, f"thread_{content_parser.data["thread_id"]}.html"
        )

        # Save HTML:
        soup_to_html_file(soup, html_file_path)

        # Content JSON creation:
        snapshot_dict_to_json(
            content_parser.data,
            scan_time_str,
            content_parser.data["thread_id"],
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
                thread_dir, 
                f"master_version_{content_parser.data["thread_id"]}.json"),
            params["site_dir"]
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

        if archive:
            # to not overload server
            # time.sleep(10)  # wait 10s before looping again
            pass
