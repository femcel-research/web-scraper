# Imports
import argparse
import glob  # Used to search for master text files in thread folder, etc.
import json
import logging
import math  # Used to get ceiling of how many threads should be duplicated
import os
import random
import shutil  # Used for copying

from datetime import datetime

def random_portion_out(
        site_params: list[dict], por_dir: str, percentage: int):
    """Portions out a random collection of TXT files from all sites passed.
    
    For every parameter file corresponding to a (scraped) site in 
    `site_params`, a random collection of human-readable text files
    are portioned out and duplicated into an accessible directory.

    The default percentage of threads portioned from each site is 10%.

    Args:
        site_params (list[dict]): List of parameter file dictionaries.
        por_dir (str): The directory portioned files should be copied into.
        percentage (int): Percentage of threads to portion out from each site.
    """
    logger = logging.getLogger(__name__)
    portion_time: str = datetime.today().strftime("%Y-%m-%dT%H:%M:%S")
    try:
        # First create the directories for the all sites where duplicates will go
        _make_site_directories(site_params, por_dir)
        logger.debug(
            "Site directories have been made for portioning")

        # Also create the directories for the current round of portioning
        current_directories: dict[str, str] = _make_get_portion_directories(
            site_params, por_dir, portion_time)
        # They are collected per site
        logger.debug(
            "Current portioning directories have been made")

        # Then collect any thread IDs which have already been duplicated
        threads_portioned_prior: dict[str, list] = _get_threads_portioned_prior(
            site_params, por_dir)
        # They are collected per site
        logger.debug(
            "Thread IDs which have been used have been collected")

        # Get the number of threads that should be duplicated for each site
        num_threads_to_duplicate: dict[str, int] = (
            _get_num_threads_to_duplicate(
                site_params, por_dir, percentage))
        # They are collected per site
        logger.debug(
            "Number of threads to duplicate per site have been collected")

        # Finally, for each site we're portioning from
        for params in site_params:
            successful_duplications: int = 0
            duplicated_thread_ids: list[str] = []
            while (  # While threads still need to be duplicated
                successful_duplications < 
                num_threads_to_duplicate[params["site_name"]]):
                # Get a random thread folder from the site
                random_thread_id = random.choice(
                    os.listdir(params["site_dir"]))
                random_thread_dir = os.path.join(
                    params["site_dir"], random_thread_id)
                
                # TODO: Add behavior for when there are no more 
                # TODO: new threads available. Current code
                # TODO: results in endless loop

                # If the thread ID hasn't been portioned before
                if random_thread_id not in (
                    threads_portioned_prior[params["site_name"]]) and (
                        random_thread_id not in duplicated_thread_ids):
                    # TODO: This should be a method...
                    if ("meta" not in random_thread_id) and (  
                        random_thread_id[0] != ".") and (
                            "logs" not in random_thread_id) and (
                                "processed" not in random_thread_id): 
                        # Copy the file over
                        print(random_thread_dir)
                        master_text_path: str = _get_a_master_text(
                            random_thread_dir)
                        if master_text_path is None:
                            continue #proceed to next random generated thread
                        else: 
                            current_portion_site_path: str = (
                                current_directories[params["site_name"]])
                            # The original text file to the directory 
                            # for the current round of portioning
                            shutil.copy(master_text_path, current_portion_site_path)

                            duplicated_thread_ids.append(random_thread_id)

                            successful_duplications += 1

            # And at last, write the duplicated IDs into site's portion log
            # "These thread IDs has now been duplicated for this site"
            _write_thread_ids_to_log(params, por_dir, duplicated_thread_ids)
    except Exception as error:
        logger.error(F"Error while portioning: {error}")
        raise Exception(f"Error while portioning: {error}")
    
def _make_site_directories(site_params: list[dict], por_dir: str):
    """Makes a directory for portioned duplicates, and a subdir per site.
    
    Raises:
        Exception: Generic exception for unanticipated errors.
    """
    try:
        if not os.path.exists(por_dir):
            os.makedirs(por_dir, exist_ok=True)
            for params in site_params:
                # Create a subdirectory for each site being scraped from
                site_por_dir: str = os.path.join(por_dir, params["site_name"])
                os.makedirs(site_por_dir, exist_ok=True)
        else:
            for params in site_params:
                site_por_dir: str = os.path.join(por_dir, params["site_name"])
                if not os.path.exists(site_por_dir):
                    os.makedirs(site_por_dir, exist_ok=True)
    except Exception as error:
        raise Exception(
            f"Error while making site directories: {error}")

def _make_get_portion_directories(
        site_params: list[dict], por_dir: str, date: str) -> dict[str, str]:
    """Makes a subdir where each site's portion will go and returns paths.

    Each path corresponds to where an individual site's duplicated threads
    will go following the portioning at runtime.
    
    Returns:
        A dictionary where the keys are site names, the values are paths. 

    Raises:
        Exception: Generic exception for unanticipated errors.   
    """
    portion_dir_paths: dict[str, str] = {}
    try:
        for params in site_params:
            site_name: str = params["site_name"]
            current_por_dir: str = os.path.join(
                por_dir, site_name, date)
            os.makedirs(current_por_dir, exist_ok=True)
            # Each directory correponds to the current round of portioning
            portion_dir_paths[params["site_name"]] = current_por_dir
        return portion_dir_paths
    except Exception as error:
        raise Exception(
            f"Error while making current portion directories: {error}")

    
def _get_threads_portioned_prior(
        site_params: list[dict], por_dir: str) -> dict[str, list]:
    """Makes a new TXT file for portioned IDs or adds IDs to dict per site.
    
    Each site (one corresponding to each dictionary in `site_params`) needs
    a log of thread IDs which have already been portioned out. If a log exists
    already, then the thread IDs are added to dictionary returned. If a log
    doesn't, a new log TXT file is made and an empty list is added to the dict.

    Returns:
        A dictionary where the keys are site names, the values are thread IDs.

    Raises:
        Exception: Generic exception for unanticipated errors.
    """
    threads_portioned_prior: dict[str, list] = {}
    # Check/make a TXT document to log already-portioned thread IDs

    # If one exists, add it to a dictionary; each key is a site name,
    # each value is a list of thread IDs which has already been duplicated
    try:
        for params in site_params:
            site_por_dir: str = os.path.join(por_dir, params["site_name"])
            por_log: str = f"{params["site_name"]}_portioned_threads_log.txt"
            por_log_path: str = os.path.join(site_por_dir, por_log)
            # Either make a new TXT file or gather IDs from existing
            if not os.path.exists(por_log_path):
                with open(por_log_path, "w") as file:
                    threads_portioned_prior[params["site_name"]] = []
                    # Don't write anything
            else:
                with open(por_log_path, "r") as file:
                    content = file.read()
                    threads_portioned_prior[params["site_name"]] = (
                        _get_logged_threads_list(content))
    except Exception as error:
        raise Exception(
            f"Error while getting used thread IDs: {error}")
    return threads_portioned_prior

def _get_logged_threads_list(log_content: str) -> list:
    """Splits the log contents to create a list of thread IDs."""
    return list(log_content.split())

def _get_num_threads_to_duplicate(
        site_params: list[dict], por_dir: str, 
        percentage: int) -> dict[str, int]:
    """Gets the number of threads which should be duplicated per site.
    
    Returns:
        A dictionary where the keys are sites, the values are num of threads.
    
    Raises:
        Exception: Generic exception for unanticipated errors.
    """
    num_threads_to_duplicate: dict[str, int] = {}
    try:
        for params in site_params:
            # site_por_dir: str = os.path.join(params[""])
            site_meta: str = f"{params["site_name"]}_meta.json"
            site_meta_path: str = os.path.join(params["site_dir"], site_meta)
            
            with open(site_meta_path, "r") as file:
                site_meta_data = json.load(file)
                # Multiply the number of threads for a site by percentage
                num_to_duplicate: int = math.ceil(
                    site_meta_data["num_sitewide_threads"] * 
                    (percentage / 100))
                num_threads_to_duplicate[params["site_name"]] = (
                    num_to_duplicate)
        return num_threads_to_duplicate
    except Exception as error:
        raise Exception(
            f"Error while getting number of threads to duplicate: {error}")

def _get_a_master_text(random_thread_dir: str) -> str:
    """Gets a path for a unspecified master text file in a thread directory.
    
    Returns:
        A path to a master text file.

    Raises:
        Exception: Generic exception for unanticipated errors.
    """
    try:
        master_text_pattern: str = os.path.join(
            random_thread_dir, "master_text_*.txt")  # Master text file
        # Glob returns list, even though we only expect one
        file = glob.glob(master_text_pattern)[0]
        return os.path.abspath(file)
            
    except Exception as error:
        return None
        # raise Exception(
        #     f"Error while getting a master text file: {error}")

def _write_thread_ids_to_log(
        specific_params: dict, por_dir: str, thread_ids: list[str]):
    """Writes the newly duplicated thread IDs to the appropriate log.
    
    Raises:
        Exception: Generic exception for unanticipated errors.
    """
    try:
        site_por_dir: str = os.path.join(
            por_dir, specific_params["site_name"])
        por_log: str = (
            f"{specific_params["site_name"]}_portioned_threads_log.txt")
        por_log_path: str = os.path.join(site_por_dir, por_log)
        with open(por_log_path, "a") as file:
            for id in thread_ids:
                file.write(f"{id}\n")
    except Exception as error:
        raise Exception(
            f"Error while writing thread IDs to log: {error}")
    
def _get_all_site_params(params_dir: str) -> list[dict]:
    """Gets a list of data from all found params files.
    
    Raises:
        Exception: Generic exception for unanticipated errors.
    """
    params_data_list: list[dict] = []
    try:
        params_file_list = glob.glob(
            os.path.join(params_dir, "*.json"))
        for params_path in params_file_list:
                # TODO: Remove check when archive scraping works
                # TODO: 4chan scraping will most likely be continuously ongoing, so I may exclude it from the portion all command for now.
                if "archive" in params_path or "4chan_" in params_path:
                        continue
                with open(params_path, "r") as params_file:
                    params: dict = json.load(params_file)
                    params_data_list.append(params)
        return params_data_list
    except Exception as error:
        raise Exception(
            F"Error while trying to load all params: {error}")

def _get_site_params(site_name: str, params_dir: str) -> list[dict]:
    """Gets a list of a single parameter file's data.
    
    Raises:
        Exception: Generic exception for unanticipated errors.
    """
    params_data_list: list[dict] = []
    try:
        params_file_list = glob.glob(
            os.path.join(params_dir, f"{site_name}*.json"))
        for params_path in params_file_list:
            with open(params_path, "r") as params_file:
                params: dict = json.load(params_file)
                # TODO: Remove check when archive scraping works
                #TODO: add conditional for 4chan
                if "archive" not in params["site_name"]:
                    params_data_list.append(params)
        return params_data_list
    except Exception as error:
        raise Exception(
            F"Error while trying to load a single site's params: {error}")

if __name__ == "__main__":
    # The default behavior is to collect a 10% portion from all found
    # param files
    parser = argparse.ArgumentParser(
        description="Generate a portion of threads.")
    parser.add_argument(
        "percentage", type=int, default=10,
        nargs='?',
        help="Percentage of threads to portion out. E.g. `10` = 10%")
    parser.add_argument(
        "por_dir", type=str, default=os.path.join(".", "data", "portions"),
        nargs='?',
        help="Directory where duplicated portions will be written to.")
    parser.add_argument(
        "site_name", type=str, default="",
        nargs='?',
        help="Name of site to portion from.")
    
    args = parser.parse_args()

    params_dir: str = os.path.join(".", "data", "params")

    if not args.por_dir:  # This will be the case if everything is default
        random_portion_out(
            _get_all_site_params(params_dir),
            args.por_dir,
            args.percentage)
    else:
        random_portion_out(
            _get_site_params(args.site_name, params_dir),
            args.por_dir,
            args.percentage)