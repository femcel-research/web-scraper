from datetime import datetime
import json
import logging
import os

logger = logging.getLogger(__name__)


class MasterMetaGenerator:
    def __init__(self, list_of_meta_paths: list[str]):
        """
        Given a list of paths to snapshot meta JSONs (gathered through Glob), a master metadata JSON is generated and saved locally.

        Args:
        list_of_meta_paths (list[str]): List containing filepaths to snapshot meta JSONs

        """
        if len(list_of_meta_paths) > 0:
            self.list_of_meta_paths: list[str] = list_of_meta_paths
            logger.info("List of snapshot meta paths retrieved.")
        else:
            logger.error("No snapshot meta paths found.")
            raise IndexError("No snapshot meta paths found.")

    def master_meta_dump(self, metadata: dict, master_meta_filepath: str) -> None:
        """Dumps thread metadata into a JSON file.

        Args:
            metadata (dict): Dictionary containing metadata values.
            master_meta_filepath (str): String containing filepath for the master meta JSON.
        """
        with open(master_meta_filepath, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def snapshot_meta_to_master_meta(self):
        """
        Transfers data from snapshot meta contents to a master metafile.
        """

        master_metadata: dict = {}
        snapshot_folder_path: str = ""
        thread_id: str = ""

        for snapshot_meta_path in self.list_of_meta_paths:
            with open(snapshot_meta_path, "r") as file:
                data = json.load(file)
            snapshot_meta = data

            # General board/thread info
            board_name: str = snapshot_meta["board_name"]
            thread_title: str = snapshot_meta["thread_title"]
            thread_id: str = snapshot_meta["thread_id"]
            url: str = snapshot_meta["url"]

            # Data relating to dates/time:
            date_published: str = snapshot_meta["date_published"]
            date_updated: str = snapshot_meta["date_updated"]
            date_scraped: str = snapshot_meta["date_scraped"]
            all_post_dates: set = set(snapshot_meta["all_post_dates"])

            # Data relating to post ids
            all_post_ids: set = set(snapshot_meta["all_post_ids"])
            num_all_post_ids: int = snapshot_meta["num_all_post_ids"]

            # Data relating to word count
            num_all_words: int = snapshot_meta["num_all_words"]

            master_metadata.update({
                "board_name": board_name,
                "thread_title": thread_title,
                "thread_id": thread_id,
                "url": url,
                "date_published": date_published,
                "date_updated": date_updated,
                "date_scraped": date_scraped,
                "all_post_dates": all_post_dates,
                "all_post_ids": all_post_ids,
                "num_all_post_ids": num_all_post_ids,
                "num_all_words": num_all_words,
            })

            snapshot_folder_path = os.path.dirname(snapshot_meta_path)

        # Pathing: Finds thread directory by finding parent folder of snapshot directory
        file_name = f"thread_meta{thread_id}.json"
        thread_folder_path = os.path.dirname(snapshot_folder_path)
        meta_file_path = os.path.join(thread_folder_path, file_name)
        
        self.master_meta_dump(master_metadata, meta_file_path)
        logger.info(f"Master metadata for thread {thread_id} has been updated.")
