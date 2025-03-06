# Imports
import datetime
import glob
import json
import os
import sys
import argparse

from .FullScrape import FullScrape
from .MetaScrape import MetaScrape
from .StatScrape import StatScrape


# TODO:
# Let command-line arguments determine what kind of scan happens?
# Improve log structure

def load_param(filepath: str):
    """Loads parameters JSON file and returns JSON load for param access.

    Args:
        filepath: Location of parameters JSON file.
    """
    try:
        with open(filepath, "r") as params:
            return json.load(params)
    except FileNotFoundError:
        return None  # TODO: Print error in log
    except json.JSONDecodeError:
        return None  # TODO: Print error in log


if __name__ == "__main__":

    # Specifies arguments for scraper.
    parser = argparse.ArgumentParser(
        prog='chan_scraper', description='Takes in arguments for a chan-style scraper.')
    parser.add_argument(
        "--scrape", help='Performs a scrape of a site homepage.')
    parser.add_argument(
        "--stat_scrape", help='Performs a statistics scrape for all threads in the data directory')
    parser.add_argument(
        "--meta_scrape", help='Reparses meta content for all HTML files in the data directory.')
    parser.add_argument(
        "--site_name", help="Specifies action to a inputted chan-style site. (Default: all)")
    args = parser.parse_args()
    scan_time = datetime.today().strftime("%Y-%m-%dT%H:%M:%S")

    # If a specific site is provided
    if args.site_name:
        # Performs a pattern-matching search; looks for something that has the words "site_name" and ".json"
        folder_path = ""  # TODO: add some dir path to where param files are stored
        param_search_path = os.path.join(
            folder_path, f'{args.site_name}*.json')
        matching_param_files = glob.glob(param_search_path, recursive=True)
        # Assumes the first matching parameter file is the one we are looking for.
        param_file_path = matching_param_files[0]
        # Load parameters JSON for use in other steps
        params = load_param(param_file_path)

        if params is None:
            pass  # TODO: Print error in log and halt

        # Assumes homepage url is stored in params file
        url = params["URL"]

        if args.scrape:
            # Perform a "full scrape"
            FullScrape.full_scrape(params, url, scan_time)
        if args.meta_scrape:
            # Perform a "meta scrape" (placeholder)
            # TODO: unsure directory structure with this var. is html content being stored in a separate folder or with its respective thread?
            temp_html_directory = ""
            MetaScrape.meta_scrape(params, temp_html_directory, scan_time)
        if args.stat_scrape:
            # Perform a "stat scrape" (placeholder)
            # TODO: unsure directory structure with this var. is json content being stored in a separate folder or with its respective thread?
            temp_json_content_directory = ""
            StatScrape.stat_scrape(
                params, temp_json_content_directory, scan_time)
    else:
        # No pattern-matching search is performed as we are using params for all sites
        directory = ""  # TODO: directory where param files are held.
        for param_file in os.listdir(directory):
            param_file_path = os.path.join(directory, param_file)
            try:
                params = load_param(param_file_path)
                # Assumes homepage url is stored in params file
                url = params["URL"]
            except:
                pass  # TODO: Print error in log and halt

            if args.scrape:
                # Perform a "full scrape"
                FullScrape.full_scrape(params, url, scan_time)
            if args.meta_scrape:
                # Perform a "meta scrape" (placeholder)
                temp_html_directory = ""
                # TODO: unsure directory structure with this var. is html content being stored in a separate folder or with its respective thread?
                MetaScrape.meta_scrape(params, temp_html_directory, scan_time)
            if args.stat_scrape:
                # Perform a "stat scrape" (placeholder)
                # TODO: unsure directory structure with this var. is json content being stored in a separate folder or with its respective thread?
                temp_json_content_directory = ""
                StatScrape.stat_scrape(
                    params, temp_json_content_directory, scan_time)

    # TODO: Sort out different behavior; different scrape classes will
    # have different utils. Everything is designed to be fully modular

    # temp_param_path = ""  # TODO: Add actual path from command-line
    # temp_html_directory = ""  # TODO: Add actual HTML directory
    # temp_json_content_directory = ""  # TODO: Add actual JSON directory
    # scan_time = datetime.datetime.today()  # .strftime("%Y-%m-%dT%H:%M:%S") 
    # # Load parameters JSON for use in other steps
    # params = load_param(temp_param_path)  # TODO: Add actual param file
    # if params is None:
    #     pass  # TODO: Print error in log and halt

    # TODO: Sort out different behavior; different scrape classes will
    # have different utils. Everything is designed to be fully modular
    # Etc.
