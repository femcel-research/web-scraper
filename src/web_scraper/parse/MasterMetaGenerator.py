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

        self.snapshot_folder_path: str = os.path.dirname(list_of_meta_paths[0])
        self.thread_id: str = ""

        self.master_metadata: dict = {
            "board_name": "",
            "thread_title": "",
            "thread_id": "",
            "url": "",
            "date_published": "",
            "date_updated": "0001-01-01T00:00:00",
            "date_scraped": "0001-01-01T00:00:00",
            "all_post_dates": set(),
            "all_post_ids": set(),
            "num_all_post_ids": 0,
            "num_all_words": 0,
        }

    def master_meta_dump(self) -> None:
        """Dumps thread metadata into a JSON file.

        Args:
            metadata (dict): Dictionary containing metadata values.
            master_meta_filepath (str): String containing filepath for the master meta JSON.
        """
        # Pathing: Finds thread directory by finding parent folder of snapshot directory
        file_name = f"thread_meta{self.thread_id}.json"
        thread_folder_path = os.path.dirname(self.snapshot_folder_path)
        master_meta_filepath = os.path.join(thread_folder_path, file_name)

        with open(master_meta_filepath, "w", encoding="utf-8") as f:
            json.dump(self.master_metadata, f, indent=2, ensure_ascii=False)

        logger.info(f"Master metadata for thread {self.thread_id} has been updated.")

    def get_master_meta(self) -> dict:
        """
        Transfers data from snapshot meta contents to a master metafile.
        """

        for snapshot_meta_path in self.list_of_meta_paths:
            with open(snapshot_meta_path, "r") as file:
                data = json.load(file)
            snapshot_meta = data

            # General board/thread info
            board_name: str = snapshot_meta["board_name"]
            thread_title: str = snapshot_meta["thread_title"]
            self.thread_id: str = snapshot_meta["thread_id"]
            url: str = snapshot_meta["url"]

            # Data relating to dates/time:
            format_string = "%Y-%m-%dT%H:%M:%S"
            date_published: str = snapshot_meta["date_published"]
            date_updated: str = snapshot_meta["date_updated"]
            date_scraped: str = snapshot_meta["date_scraped"]
            all_post_dates: set = set(snapshot_meta["all_post_dates"])

            # Data relating to post ids
            all_post_ids: set = set(snapshot_meta["all_post_ids"])
            num_all_post_ids: int = snapshot_meta["num_all_post_ids"]

            # Data relating to word count
            num_all_words: int = snapshot_meta["num_all_words"]

            # Updating update/scrape dates if there exists a newer one:
            updated_datetime_obj = datetime.strptime(date_updated, format_string)
            current_updated = datetime.strptime(
                self.master_metadata["date_updated"], format_string
            )
            # If there was a later update, replace the update date
            if updated_datetime_obj > current_updated:
                self.master_metadata.update({"date_updated": date_updated})

            scraped_datetime_obj = datetime.strptime(date_scraped, format_string)
            current_scraped = datetime.strptime(
                self.master_metadata["date_scraped"], format_string
            )
            # If there was a later scrape, replace the scrape date
            if scraped_datetime_obj > current_scraped:
                self.master_metadata.update({"date_scraped": date_scraped})

            # This should be the same throughout all snapshots
            self.master_metadata.update(
                {
                    "board_name": board_name,
                    "thread_title": thread_title,
                    "thread_id": self.thread_id,
                    "url": url,
                    "date_published": date_published,
                    "date_updated": date_updated,
                    "date_scraped": date_updated,
                    "all_post_dates": all_post_dates,
                    "all_post_ids": all_post_ids,
                    "num_all_post_ids": num_all_post_ids,
                    "num_all_words": num_all_words,
                }
            )

        return self.master_metadata
