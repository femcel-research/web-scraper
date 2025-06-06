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
        self.master_meta_filepath = os.path.join(thread_folder_path, file_name)

        master_meta = self.generate_master_meta()

        with open(self.master_meta_filepath, "w", encoding="utf-8") as f:
            json.dump(master_meta, f, indent=2, ensure_ascii=False)

        logger.info(f"Master metadata for thread {self.thread_id} has been updated.")

    def get_path(self) -> str:
        return self.master_meta_filepath

    def generate_master_meta(self) -> dict:
        """
        Transfers data from snapshot meta contents to a master metafile.
        """

        for i, snapshot_meta_path in enumerate(self.list_of_meta_paths):
            with open(snapshot_meta_path, "r") as file:
                data = json.load(file)
            snapshot_meta = data

            # General board/thread info
            if i == 0:
                self.master_metadata["board_name"] = snapshot_meta["board_name"]
                self.master_metadata["thread_title"] = snapshot_meta["thread_title"]
                self.thread_id: str = snapshot_meta["thread_id"]
                self.master_metadata["thread_id"] = self.thread_id
                self.master_metadata["url"] = snapshot_meta["url"]
                self.master_metadata["date_published"] = snapshot_meta["date_published"]

            # Data relating to dates/time:
            format_string = "%Y-%m-%dT%H:%M:%S"
            snapshot_date_updated: str = snapshot_meta["date_updated"]
            snapshot_date_scraped: str = snapshot_meta["date_scraped"]

            # Convert snapshot dates to datetime objs for comparison
            snapshot_updated_datetime_obj = datetime.strptime(
                snapshot_date_updated, format_string
            )
            snapshot_scraped_datetime_obj = datetime.strptime(
                snapshot_date_scraped, format_string
            )

            # Convert master dates to datetime objs for comparison
            master_updated_datetime_obj = datetime.strptime(
                self.master_metadata["date_updated"], format_string
            )
            master_scraped_datetime_obj = datetime.strptime(
                self.master_metadata["date_scraped"], format_string
            )

            if snapshot_updated_datetime_obj > master_updated_datetime_obj:
                self.master_metadata["date_updated"] = snapshot_meta["date_updated"]
                logger.debug(
                    f"Updated master date_updated to {snapshot_date_updated} from: {snapshot_meta_path}"
                )

            if snapshot_scraped_datetime_obj > master_scraped_datetime_obj:
                self.master_metadata["date_scraped"] = snapshot_meta["date_scraped"]
                logger.debug(
                    f"Updated master date_scraped to {snapshot_date_scraped} from: {snapshot_meta_path}"
                )
                # Aggregate sets
                self.master_metadata["all_post_dates"].update(
                    snapshot_meta["all_post_dates"]
                )
                logger.debug(
                    f"Updated master all_post_dates to {snapshot_meta["all_post_dates"]} from: {snapshot_meta_path}"
                )
                self.master_metadata["all_post_ids"].update(
                    snapshot_meta["all_post_ids"]
                )
                logger.debug(
                    f"Updated master all_post_ids to {snapshot_meta["all_post_ids"]} from: {snapshot_meta_path}"
                )

                # Update counts: compares current master & snapshot and takes the max
                latest_post_count: int = max(
                    self.master_metadata["num_all_post_ids"],
                    snapshot_meta["num_all_post_ids"],
                )
                self.master_metadata["num_all_post_ids"] = latest_post_count
                logger.debug(
                    f"Updated master num_all_post_ids to {latest_post_count} from: {snapshot_meta_path}"
                )

                latest_num_count: int = max(
                    self.master_metadata["num_all_words"],
                    snapshot_meta["num_all_words"],
                )
                self.master_metadata["num_all_words"] = latest_num_count
                logger.debug(
                    f"Updated master num_all_words to {latest_num_count} from: {snapshot_meta_path}"
                )

        return self.master_metadata
