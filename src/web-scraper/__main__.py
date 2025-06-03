# Imports
import argparse
import glob
import json
import logging
import sys

from datetime import datetime
from pathlib import Path

scan_time_str = datetime.today().strftime("%Y-%m-%dT%H:%M:%S")  # ISO format

# Ensure the logs directory exists
log_dir = Path("./logs")
log_dir.mkdir(parents=True, exist_ok=True)

# Root logger config
logging.basicConfig(
    filename=(f"./logs/{scan_time_str}.log"),
    filemode="w",
    format=("%(asctime)s %(levelname)s : %(message)s"),  
    datefmt="%Y-%m-%dT%H:%M:%S",
    style="%",
    level=logging.DEBUG,  # We can make a lot of the spam-y logs DEBUG
)
logger = logging.getLogger(__name__)
logger.info("Root logger configured")

# Arguments
parser = argparse.ArgumentParser(
    prog="web-scraper",
    description=("A web scraper and parser for (currently) chan-style "
        "websites, built around a passed parameters file.\n"
        "By default, URLs are pulled from the homepage specified "
        "in the provided parameters file, then they are parsed "
        "in accordance with the README, and saved to the relative "
        "directory in the passed parameters file."),
        formatter_class=argparse.RawTextHelpFormatter)

# Name of the parameters file; a glob search will be used to retrieve locally
parser.add_argument(
    "params_name",
    help="Name of the JSON parameters file to be searched and retrieved."
)

args = parser.parse_args()

# Parameters
params_file_list = glob.glob(f"./params/{args.params_name}*.json")

params_file = params_file_list[0] if params_file_list else None

if params_file is None:
    logger.critical(f"Parameters file name is not valid: {args.params_name}")
    logger.critical("Aborting")
    sys.exit(1)
else:
    logger.debug(f"Parameters file name is valid: {args.params_name}")  
    logger.debug("Choosing the first file containing the name")

params_path = Path(params_file)

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
        f"An unexpected error occurred while loading parameters: {error}")
    logger.critical("Aborting")
    sys.exit(1)