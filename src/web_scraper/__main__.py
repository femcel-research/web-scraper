# Imports
import argparse
import glob
import json
import logging
import sys

from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

from fetch import fetch_html_content
from scrape import HomepageScraper
from parse.HTMLToContent import ChanToContent
from parse.MasterContentGenerator import MasterContentGenerator
from parse.MasterMetaGenerator import MasterMetaGenerator
from parse.SnapshotMetaGenerator import SnapshotMetaGenerator
from parse.SiteMetaGenerator import SiteMetaGenerator

from write_out import *

scan_time_str = datetime.today().strftime("%Y-%m-%dT%H:%M:%S")  # ISO format

# Ensure the logs directory exists
log_dir = Path("./data/logs")
log_dir.mkdir(parents=True, exist_ok=True)

# Root logger config
logging.basicConfig(
    filename=(f"./data/logs/{scan_time_str}.log"),
    filemode="w",
    format=("%(asctime)s %(levelname)s : %(message)s"),
    datefmt="%Y-%m-%dT%H:%M:%S",
    style="%",
    level=logging.INFO,  # We can make a lot of the spam-y logs DEBUG
)
logger = logging.getLogger(__name__)
logger.info("Root logger configured")

# Arguments
parser = argparse.ArgumentParser(
    prog="web_scraper",
    description=(
        "A web scraper and parser for (currently) chan-style "
        "websites, built around a passed parameters file.\n"
        "By default, URLs are pulled from the homepage specified "
        "in the provided parameters file, then they are parsed "
        "in accordance with the README, and saved to the relative "
        "directory in the passed parameters file."
    ),
    formatter_class=argparse.RawTextHelpFormatter,
)

# Name of the parameters file; a glob search will be used to retrieve locally
parser.add_argument(
    "params_name", help="Name of the JSON parameters file to be searched and retrieved."
)

args = parser.parse_args()

# Parameters
params_file_list = glob.glob(f"./data/params/{args.params_name}*.json")

params_file = params_file_list[0] if params_file_list else None

if params_file is None:
    logger.critical(f"Parameters file name is not valid: {args.params_name}")
    logger.critical("Aborting")
    sys.exit(1)
else:
    logger.debug(f"Parameters file name is valid: {args.params_name}")
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
    logger.critical(f"An unexpected error occurred while loading parameters: {error}")
    logger.critical("Aborting")
    sys.exit(1)

homepage: bytes = fetch_html_content(params["hp_url"])
scraper: HomepageScraper = HomepageScraper(
    homepage, params["domain"], params["container"]
)
url_list: list[str] = scraper.homepage_to_list()
for url in url_list:
    soup = BeautifulSoup(fetch_html_content(url), features="html.parser")
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
        f"./data/{args.params_name}", content_parser.data["thread_id"]
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
        f"./data/{args.params_name}",
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
        list_of_snapshot_contents
    )
    master_content_generator.content_dump()

    # Master meta creation:
    candidate_meta_files = os.path.join(thread_dir, "**", "meta_*.json")
    list_of_snapshot_metas: list[str] = list(
        glob.glob(candidate_meta_files, recursive=True)
    )
    master_meta_generator: MasterMetaGenerator = MasterMetaGenerator(
        list_of_snapshot_metas
    )
    master_meta_generator.master_meta_dump()
    
    # Update site meta:
    site_meta_generator: SiteMetaGenerator = SiteMetaGenerator(args.params_name)
    site_meta_generator.dump_site_meta()
