import argparse
import glob
import json
import logging
import os

logger = logging.getLogger(__name__)


def get_site_stats(site_name) -> dict:
    """
    Iterates through a list of master meta paths found in the site data subdirectory, and returns a dictionary of site-wide statistics to be dumped into a JSON.
    """
    master_meta_pattern = "**/thread_meta_*.json"
    site_dir = os.path.join("./data", site_name)
    search_pattern = os.path.join(site_dir, master_meta_pattern)
    list_of_master_metas: list[str] = glob.glob(search_pattern, recursive=True)

    if len(list_of_master_metas) > 0:
        first_found_meta_path = list_of_master_metas[0]
        with open(first_found_meta_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        first_found_meta = data
        try:
            url: str = first_found_meta["url"]
        except KeyError:
            # Old meta key
            url: str = first_found_meta["URL"]

        masterdata = {
            "url": url,
            "site_title": site_name,
            # "description": "", Unsure if we are using these. If so, TODO: will need to add description/keyword rtrieval in ChanScraper
            # "keywords": "",
        }

        stats: dict = calculate_stats(list_of_master_metas)
        masterdata.update(stats)
        return masterdata
    else:
        logger.error("No master_meta paths found.")
        raise IndexError("No master_meta paths found.")


def calculate_stats(list_of_master_metas: list[str]) -> dict:
    """Calculates sitewide stats by iterating through every master meta within the site's data subfolder.
    Args:
        list_of_master_metas (list[str]): List containing filepaths to each master meta within the site's data subfolder
    """
    num_sitewide_threads: int = len(
        list_of_master_metas
    )  # Assumption that number of sitewide threads should correlate with the number of master_thread metas found within a site's data subfolder.
    num_sitewide_total_posts: int = 0
    num_sitewide_dist_posts: int = 0

    # Updates values for num_sitewide_total_posts and num_sitewide_dist_posts
    for master_meta_path in list_of_master_metas:
        with open(master_meta_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        master_meta = data
        try:
            num_sitewide_total_posts += master_meta["num_aggregate_post_ids"]
        except KeyError:
            # Old meta key
            num_sitewide_total_posts += master_meta["num_total_posts"]

        try:
            num_sitewide_dist_posts += master_meta["num_unique_post_ids"]
        except KeyError:
            # Old meta key
            num_sitewide_dist_posts += master_meta["num_dist_posts"]

    return {
        "num_sitewide_threads": num_sitewide_threads,
        "num_sitewide_total_posts": num_sitewide_total_posts,
        "num_sitewide_dist_posts": num_sitewide_dist_posts,
    }


def dump_site_meta(site_name):
    """
    Recalculates and saves the current site statistics to its respective site folder.
    Args:
        site_name (str): Name of site
    """
    site_meta_file_path = os.path.join("./data", site_name, f"{site_name}_meta.json")
    masterdata: dict = get_site_stats(site_name)

    os.makedirs(os.path.dirname(site_meta_file_path), exist_ok=True)
    with open(site_meta_file_path, "w") as json_file:
        json.dump(masterdata, json_file, indent=2)


def dump_all():
    """
    Recalculates and saves up-to-date site statistics for all sites.
    """
    params_directory = os.path.join("./data", "params")
    params_files: list[str] = os.listdir(params_directory)
    # Iterates through all availiable sites and recalculates their stats
    for param_file in params_files:
        site_name = param_file.replace("_params.json", "")
        if "archive" in site_name or "4chan_" in site_name:  # TODO: Remove once archive sites work
            continue
        else:
            dump_site_meta(site_name)


if __name__ == "__main__":  # used to run script as executable
    parser = argparse.ArgumentParser(
        description="Recalculates sitewide statistics. If no site_name is entered, all sites are recalculated."
    )
    parser.add_argument(
        "site_name",
        type=str,
        nargs="?",
        help="Name of the site data folder",
    )
    args = parser.parse_args()

    if args.site_name is None:
        dump_all()

    else:
        dump_site_meta(args.site_name)
