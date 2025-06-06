import argparse
import glob
import logging
import os
from HTMLToContent.ChanToContent import ChanToContent
from .SnapshotMetaGenerator import SnapshotMetaGenerator
from .MasterContentGenerator import MasterContentGenerator
from .MasterMetaGenerator import MasterMetaGenerator

logger = logging.getLogger(__name__)


class Reparser:
    def __init__(self):
        """Reparses data within data subfolder"""
        pass

    def regenerate_masters(thread_folder_path: str) -> None:
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

    def reparse_site(self, site_name):
        """Processes existing files present within a site's data subfolder."""
        directory = f"./data/{site_name}"
        html_pattern = "*.html"  # Look for an html file
        logger.info("Processing existing threads")  # Log message

        for thread_folder in os.listdir(directory):
            thread_folder_path = os.path.join(directory, thread_folder)

            # If the thread folder is a directory, find its newest .html and meta file and use that to reprocess the thread.
            if os.path.isdir(thread_folder_path):
                html_search_path = os.path.join(thread_folder_path, "**", html_pattern)
                matching_html_files = glob.glob(html_search_path, recursive=True)

                if len(matching_html_files) > 0:
                    # Reparse all snapshots to fit new format
                    for html in matching_html_files:
                        # Content creation:
                        # TODO: Currently we have the HTML, implement pipeline: turning it into content, then meta, then updating masters
                        content_generator = (
                            ChanToContent()
                        )  # have to have logic tree for diff sites?
                        content_path: str = (
                            ""  # TODO: implement a getter for the newly created content.json path (easier than globbing)
                        )
                        logger.debug(
                            f"Snapshot content has been generated for HTML path: {html}"
                        )  # Log message

                        # Snapshot meta creation:
                        meta_generator = SnapshotMetaGenerator(content_path)
                        meta_generator.meta_dump()
                        logger.debug(
                            f"Snapshot meta has been generated for content path: {content_path}"
                        )  # Log message

                    # Regenerates masters
                    self.regenerate_masters(thread_folder_path)

    def reparse_all(self):
        """Reparses all data for all sites"""
        data_directory = f"./data"
        # Iterates through all directories in data and reparses their data
        # The following assumes all directories in the data subfolder are site_folders.
        for site_folder in os.listdir(data_directory):
            self.reparse_site(site_folder)


if __name__ == "__main__":  # used to run script as executable
    parser = argparse.ArgumentParser(description="Reparses data. If no site_name is entered, all data is reparsed.")
    parser.add_argument(
        "site_name", type=str, help="Name of the site data folder (e.g., crystal.cafe)"
    )
    args = parser.parse_args()
    reparser = Reparser()

    if args.site_name is None:
        reparser.reparse_all()

    else:
        reparser.reparse_site(args.site_name)