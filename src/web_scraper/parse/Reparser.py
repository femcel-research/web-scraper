import argparse
import datetime
import glob
import json
import logging
import os
from bs4 import BeautifulSoup

# Imports if running through terminal
from ..write_out import *
from .HTMLToContent.ChanToContent import ChanToContent
from .SnapshotMetaGenerator import SnapshotMetaGenerator
from .MasterContentGenerator import MasterContentGenerator
from .MasterMetaGenerator import MasterMetaGenerator
from .SiteMetaGenerator import SiteMetaGenerator

# Imports if running debugger 
# from web_scraper.write_out import *
# from web_scraper.parse.HTMLToContent.ChanToContent import ChanToContent
# from web_scraper.parse.SnapshotMetaGenerator import SnapshotMetaGenerator
# from web_scraper.parse.MasterContentGenerator import MasterContentGenerator
# from web_scraper.parse.MasterMetaGenerator import MasterMetaGenerator

logger = logging.getLogger(__name__)


class Reparser:
    def __init__(self):
        """Reparses data within data subfolder"""
        pass

    def regenerate_masters(self, thread_folder_path: str) -> None:
        """Regenerates master_content and master_meta files
        Args:
            thread_folder_path (str): String containing filepath of thread folder"""

        # Find all of thread's content JSONs
        candidate_content_files = os.path.join(
            thread_folder_path, "**", "content_*.json"
        )
        list_of_content_paths: list[str] = list(
            glob.glob(candidate_content_files, recursive=True)
        )

        # Regenerate thread's master content
        master_content_generator = MasterContentGenerator(list_of_content_paths)
        master_content_generator.content_dump()
        logger.info(
            f"Master content has been regenerated for thread path: {thread_folder_path}"
        )  # Log message

        # Find all of thread's meta JSONs
        candidate_meta_files = os.path.join(thread_folder_path, "**", "meta_*.json")
        list_of_meta_paths: list[str] = list(
            glob.glob(candidate_meta_files, recursive=True)
        )

        # Regenerate thread's master meta
        master_meta_generator = MasterMetaGenerator(list_of_meta_paths)
        master_meta_generator.master_meta_dump()
        logger.info(
            f"Master meta has been regenerated for thread path: {thread_folder_path}"
        )  # Log message

    def generate_content(self, html: str, site_name: str, scan_time: str) -> str:
        """Generates a content JSON from saved HTML and returns the file path.
        Args:
            scan_time_str (str): String containing scan time
            html (str): String containing HTML
            site_name (str): String containing site_name. Spelling must corresponds to the site's data subfolder name.

        Returns:
            content_file_path (str): String containing the filepath for the generated content file.
        """
        # Content creation: TODO: use thread scan name for scan time str, just get dir name of html file
        params_file_list = glob.glob(f"./data/params/{site_name}*.json")
        params_path = params_file_list[0]
        with open(params_path, "r") as params_file:
            params = json.load(params_file)

        html_soup = BeautifulSoup(html, features="html.parser")
        content_parser = ChanToContent(
            scan_time,
            html_soup,
            "",
            params["op_class"],
            params["reply_class"],
            params["root_domain"],
        )
        snapshot_dict_to_json(
            content_parser.data,
            scan_time,
            content_parser.data["thread_id"],
            "content",
            f"./data/{site_name}",
        )

        thread_data_path: str = os.path.join(
            f"./data/{site_name}", content_parser.data["thread_id"], scan_time
        )
        os.makedirs(thread_data_path, exist_ok=True)
        content_filepath: str = os.path.join(
            thread_data_path, f"content_{content_parser.data["thread_id"]}.json"
        )
        return content_filepath

    def reparse_site(self, site_name):
        """Processes existing files present within a site's data subfolder."""

        # Pathing & param retrieval
        directory = f"./data/{site_name}"

        html_pattern = "*.html"  # Look for an html file
        logger.info("Processing existing threads")  # Log message

        for thread_folder in os.listdir(directory):
            thread_folder_path = os.path.join(directory, thread_folder)

            # If the thread folder is a directory, find its .html and meta file and use that to reprocess the thread.
            if os.path.isdir(thread_folder_path):
                html_search_path = os.path.join(thread_folder_path, "**", html_pattern)

                matching_html_files = glob.glob(html_search_path, recursive=True)

                if len(matching_html_files) > 0:
                    site_meta_generator: SiteMetaGenerator = SiteMetaGenerator(site_name)
                    # Reparse all snapshots to fit new format
                    for html_file_path in matching_html_files:
                        html_dir_name: str = os.path.dirname(html_file_path)
                        html_scan_time: str = os.path.basename(
                            html_dir_name
                        )  # assumption that html is stored in a scan_time subfolder
                        with open(html_file_path, "r", encoding="utf-8") as f:
                            html_content = f.read()

                        # Generate content and then pass to SnapshotMetaGenerator
                        content_path: str = self.generate_content(
                            html_content, site_name, html_scan_time
                        )
                        logger.debug(
                            f"Snapshot content has been generated for HTML path: {html_file_path}"
                        )  # Log message # Snapshot meta creation:]
                        meta_generator = SnapshotMetaGenerator(content_path)
                        meta_generator.meta_dump()
                        logger.debug(
                            f"Snapshot meta has been generated for content path: {content_path}"
                        )  # Log message

                    # Regenerates masters
                    self.regenerate_masters(thread_folder_path)
                    # Update site meta
                    site_meta_generator.dump_site_meta()
        
        

    def reparse_all(self):
        """Reparses all data for all sites"""
        data_directory = f"./data"
        # Iterates through all directories in data and reparses their data
        # The following assumes all directories in the data subfolder are site_folders.
        for site_folder in os.listdir(data_directory):
            self.reparse_site(site_folder)


if __name__ == "__main__":  # used to run script as executable
    parser = argparse.ArgumentParser(
        description="Reparses data. If no site_name is entered, all data is reparsed."
    )
    parser.add_argument(
        "site_name",
        type=str,
        nargs="?",
        help="Name of the site data folder (e.g., crystal.cafe)",
    )
    args = parser.parse_args()
    reparser = Reparser()

    if args.site_name is None:
        reparser.reparse_all()

    else:
        reparser.reparse_site(args.site_name)
