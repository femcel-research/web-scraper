import argparse
import datetime
import glob
import json
import logging
import os
from bs4 import BeautifulSoup

# Imports if running through terminal
from ..write_out import *
from . import MasterTextGenerator
from .HTMLToContent.ChanToContent import ChanToContent
from .JSONToContent.SourceToContent import SourceToContent
from .SnapshotMetaGenerator import SnapshotMetaGenerator
from .MasterContentGenerator import MasterContentGenerator
from .MasterMetaGenerator import MasterMetaGenerator

# Imports if running debugger
# from web_scraper.write_out import *
# from web_scraper.parse.HTMLToContent.ChanToContent import ChanToContent
# from web_scraper.parse.JSONToContent.SourceToContent import SourceToContent
# from web_scraper.parse.SnapshotMetaGenerator import SnapshotMetaGenerator
# from web_scraper.parse.MasterContentGenerator import MasterContentGenerator
# from web_scraper.parse.MasterMetaGenerator import MasterMetaGenerator
# from web_scraper.parse.MasterTextGenerator import MasterTextGenerator


logger = logging.getLogger(__name__)


class Reparser:
    def __init__(self):
        """Reparses data within data subfolder"""
        pass

    def regenerate_masters(self, thread_folder_path: str, params: dict) -> None:
        """Regenerates master_content and master_meta files
        Args:
            thread_folder_path (str): String containing filepath of thread folder
            params (dict): Parameters, used in master_text_generation
        """

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

        # Master text creation:
        thread_id: str = master_content_generator.master_contents["thread_id"]
        # Not sure how else to get this because I don't really
        # understand this pipeline?
        master_text_generator: MasterTextGenerator = MasterTextGenerator(
            os.path.join(thread_folder_path, f"master_version_{thread_id}.json"),
            params["site_dir"],
        )
        master_text_generator.write_text()

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

    def generate_content(
        self, html: str, site_name: str, scan_time: str, params: dict
    ) -> str:
        """Generates a content JSON from saved HTML and returns the file path.
        Args:
            scan_time_str (str): String containing scan time
            html (str): String containing HTML
            site_name (str): String containing site_name. Spelling must corresponds to the site's data subfolder name.

        Returns:
            content_file_path (str): String containing the filepath for the generated content file.
        """
        # Content creation:
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
    
    def generate_fourchan_content(
        self, source_json: dict, site_name: str, scan_time: str, params: dict
    ) -> str:
        """Generates a content JSON from saved HTML and returns the file path.
        Args:
            scan_time_str (str): String containing scan time
            html (str): String containing HTML
            site_name (str): String containing site_name. Spelling must corresponds to the site's data subfolder name.

        Returns:
            content_file_path (str): String containing the filepath for the generated content file.
        """
        # Content creation:
        board_name = params["board_name"]
        content_parser = SourceToContent(board_name, source_json, scan_time)

        #File creation
        site_dir = params["site_dir"]
        snapshot_dict_to_json(
            content_parser.data,
            scan_time,
            content_parser.data["thread_id"],
            "content",
            site_dir,
        )

        thread_data_path: str = os.path.join(
            f"./data/{site_name}", content_parser.data["thread_id"], scan_time
        )
        os.makedirs(thread_data_path, exist_ok=True)
        content_filepath: str = os.path.join(
            thread_data_path, f"content_{content_parser.data["thread_id"]}.json"
        )
        return content_filepath

    def reparse_site(self, site_search):
        """Processes existing files present within a site's data subfolder."""
        try:
            # Param retrieval
            params_file_list = glob.glob(f"./data/params/{site_search}*.json")
            params_path = params_file_list[0]
            with open(params_path, "r") as params_file:
                params = json.load(params_file)

            # Pathing
            site_name: str = params["site_name"]
            site_directory = f"./data/{site_name}"

            html_pattern = "*.html"  # Look for an html file
            logger.info("Processing existing threads")  # Log message

            for thread_folder in os.listdir(site_directory):
                thread_folder_path = os.path.join(site_directory, thread_folder)

                # If the thread folder is a directory, find its .html and meta file and use that to reprocess the thread.
                if os.path.isdir(thread_folder_path):
                    html_search_path = os.path.join(
                        thread_folder_path, "**", html_pattern
                    )

                    matching_html_files = glob.glob(html_search_path, recursive=True)

                    if len(matching_html_files) > 0:
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
                                html_content, site_name, html_scan_time, params
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
                        self.regenerate_masters(thread_folder_path, params)
        except FileNotFoundError as error:
            logger.error(f"Error while reparsing: {error}")
            pass
        except Exception as error:
            logger.error(f"Error while reparsing: {error}")
            pass

    def reparse_all(self):
        """Reparses all data for all sites"""
        params_directory = os.path.join("./data", "params")
        params_files: list[str] = os.listdir(params_directory)
        # Iterates through all availiable sites and reparses the respective site data
        for param_file in params_files:
            site_name = param_file.replace("_params.json", "")
            if ("4chan_" in  site_name):
                self.reparse_fourchan(site_name)
            else:
                self.reparse_site(site_name)

    def reparse_fourchan(self, board_search):
        """Reparses data for /lgbt/"""
        try:
            # Param retrieval
            params_file_list = glob.glob(f"./data/params/{board_search}*.json")
            params_path = params_file_list[0]
            with open(params_path, "r") as params_file:
                params = json.load(params_file)

            # Pathing
            site_name: str = params["site_name"]
            board_name: str = params["board_name"]
            site_directory = f"./data/{site_name}"

            source_pattern = "source*.json"  # Look for an html file
            logger.info("Processing existing threads")  # Log message

            for thread_folder in os.listdir(site_directory):
                thread_folder_path = os.path.join(site_directory, thread_folder)

                # If the thread folder is a directory, find its source .json and meta file and use that to reprocess the thread.
                if os.path.isdir(thread_folder_path):
                    source_search_path = os.path.join(
                        thread_folder_path, "**", source_pattern
                    )

                    matching_source_files = glob.glob(
                        source_search_path, recursive=True
                    )

                    if len(matching_source_files) > 0:
                        # Reparse all snapshots to fit new format
                        for source_file_path in matching_source_files:
                            source_dir_name: str = os.path.dirname(source_file_path)
                            source_scan_time: str = os.path.basename(
                                source_dir_name
                            )  # assumption that html is stored in a scan_time subfolder

                            with open(source_file_path, "r", encoding="utf-8") as file:
                                source_content: dict = json.load(file)

                            # Generate content and then pass to SnapshotMetaGenerator
                            content_path: str = self.generate_fourchan_content(
                                source_content, site_name, source_scan_time, params
                            )
                            logger.debug(
                                f"Snapshot content has been generated for HTML path: {source_file_path}"
                            )  # Log message # Snapshot meta creation:]
                            meta_generator = SnapshotMetaGenerator(content_path)
                            meta_generator.meta_dump()
                            logger.debug(
                                f"Snapshot meta has been generated for content path: {content_path}"
                            )  # Log message

                        # Regenerates masters
                        self.regenerate_masters(thread_folder_path, params)
        except FileNotFoundError as error:
            logger.error(f"Error while reparsing: {error}")
            pass
        except Exception as error:
            logger.error(f"Error while reparsing: {error}")
            pass


if __name__ == "__main__":  # used to run script as executable
    parser = argparse.ArgumentParser(
        description="Reparses data. If no site_name is entered, all data is reparsed."
    )
    parser.add_argument(
        "site_name",
        type=str,
        nargs="?",
        help="Name of the site data folder",
    )
    args = parser.parse_args()
    reparser = Reparser()

    if args.site_name is None:
        reparser.reparse_all()

    elif "4chan_" in args.site_name:
        reparser.reparse_fourchan(args.site_name)

    else:
        reparser.reparse_site(args.site_name)
