# Imports
import argparse
import logging

from datetime import datetime
from pathlib import Path
from scrape_and_parse import *
from fourchan_scrape_and_parse import *

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
    "params_name", nargs="?", help="Name of the JSON parameters file to be searched and retrieved."
)

parser.add_argument(
    "backlog", nargs="?", type=bool, help="Boolean used to determine whether or not 4chan backlog is scraped."
)

args = parser.parse_args()

if args.params_name is None:
    scrape_all(scan_time_str)

elif "4chan_" in args.params_name: #to differentiate from 4chanarchives
    if args.backlog is not None:
        fourchan_backlog_scrape(args.params_name, scan_time_str)
    else:
        fourchan_scrape(args.params_name, scan_time_str)
else:
    scrape(args.params_name, scan_time_str)