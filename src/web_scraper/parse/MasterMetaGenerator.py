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
        snapshot_history: dict = {} 
        recent_word_count = self.find_recent_word_count()  

        self.master_metadata: dict = {
            "board_name": "",
            "thread_title": "",
            "thread_id": "",
            "url": "",
            "date_published": "",
            "most_recent_update_date": "0001-01-01T00:00:00",
            "most_recent_scrape_date": "0001-01-01T00:00:00",
            "all_post_dates": set(),
            "all_update_dates": set(),
            "all_scrape_dates": set(),
            "snapshot_history": snapshot_history,
            "num_aggregate_post_ids": 0,
            "unique_post_ids": set(),
            "num_unique_post_ids": 0,
            "lost_post_ids": set(),
            "num_aggregate_words": 0,
            "num_words_most_recent": recent_word_count
        }

    def master_meta_dump(self) -> None:
        """Dumps thread metadata into a JSON file.

        Args:
            metadata (dict): Dictionary containing metadata values.
            master_meta_filepath (str): String containing filepath for the master meta JSON.
        """
        # Pathing: Finds thread directory by finding parent folder of snapshot directory
        master_meta = self._generate_master_meta()
        thread_id = self.master_metadata["thread_id"]
        file_name = f"thread_meta_{thread_id}.json"
        thread_folder_path = os.path.dirname(self.snapshot_folder_path)
        self.master_meta_filepath = os.path.join(thread_folder_path, file_name)

        with open(self.master_meta_filepath, "w", encoding="utf-8") as f:
            json.dump(master_meta, f, indent=2, ensure_ascii=False)

        logger.info(f"Master metadata for thread {thread_id} has been updated.")

    def get_path(self) -> str:
        """Retrieves master meta filepath"""
        return self.master_meta_filepath
    
    def find_recent_word_count(self) -> int:
        """Finds word count from the most recent snapshot."""
        most_recent_snapshot = max(self.list_of_meta_paths, key=os.path.getmtime)
        with open(most_recent_snapshot, "r") as file:
                data = json.load(file)
        snapshot_meta = data
        num_words_most_recent: int = int(snapshot_meta["num_all_words"])
        return num_words_most_recent


    def find_lost_ids(self, snapshot_meta: dict) -> dict:
        """Given a snapshot meta, it returns a set containing its lost IDs
        Args:
            snapshot_meta (dict): Dictionary containing data from snapshot meta"""
        lost_ids: set = set()
        snapshot_ids = set((snapshot_meta["all_post_ids"]))
        unique_post_ids = self.master_metadata["unique_post_ids"]
        for post_id in unique_post_ids:
            if post_id not in snapshot_ids:
                lost_ids.add(post_id)
        return lost_ids

    def _generate_master_meta(self) -> dict:
        """
        Transfers data from snapshot meta contents to a master metafile.
        """

        num_aggregate_post_ids = 0
        num_lost_post_ids = 0

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

            # Aggregate sets
            logger.debug(
                f"Updated master all_update_dates with {snapshot_meta["date_updated"]} from: {snapshot_meta_path}"
            )
            # All post IDs:
            self.master_metadata["unique_post_ids"].update(
                snapshot_meta["all_post_ids"]
            )
            logger.debug(
                f"Updated master unique_post_ids to {snapshot_meta["all_post_ids"]} from: {snapshot_meta_path}"
            )
            # Finds lost IDs & updates master
            lost_post_ids: set = set(self.find_lost_ids(snapshot_meta))
            self.master_metadata["lost_post_ids"].update(lost_post_ids)
            num_lost_post_ids += len(lost_post_ids)
            logger.debug(
                f"Updated master lost_post_ids with {lost_post_ids} from: {snapshot_meta_path}"
            )

            # All post dates:
            self.master_metadata["all_post_dates"].update(
                snapshot_meta["all_post_dates"]
            )
            logger.debug(
                f"Updated master all_post_dates with {snapshot_meta["all_post_dates"]} from: {snapshot_meta_path}"
            )

            # All update dates:
            self.master_metadata["all_update_dates"].update(
                [snapshot_date_updated]
            )
            logger.debug(
                f"Updated master all_post_dates with {snapshot_date_updated} from: {snapshot_meta_path}"
            )


            # All scrape dates:
            self.master_metadata["all_scrape_dates"].update(
                ([snapshot_date_scraped])
            )
            logger.debug(
                f"Updated master all_scrape_dates with {snapshot_date_scraped} from: {snapshot_meta_path}"
            )

            # Update snapshot history:
            self.master_metadata["snapshot_history"].update(
                {snapshot_date_scraped: snapshot_meta["all_post_ids"]}
            )
            logger.debug(
                f"Updated master snapshot_history with { {snapshot_date_scraped: snapshot_meta["all_post_ids"]}} from: {snapshot_meta_path}"
            )

            # Convert snapshot dates to datetime objs for comparison
            snapshot_updated_datetime_obj = datetime.strptime(
                snapshot_date_updated, format_string
            )
            snapshot_scraped_datetime_obj = datetime.strptime(
                snapshot_date_scraped, format_string
            )

            # Convert master dates to datetime objs for comparison
            master_updated_datetime_obj = datetime.strptime(
                self.master_metadata["most_recent_update_date"], format_string
            )
            master_scraped_datetime_obj = datetime.strptime(
                self.master_metadata["most_recent_scrape_date"], format_string
            )

            if snapshot_updated_datetime_obj > master_updated_datetime_obj:
                self.master_metadata["most_recent_update_date"] = snapshot_meta[
                    "date_updated"
                ]
                logger.debug(
                    f"Updated master most_recent_update_date to {snapshot_date_updated} from: {snapshot_meta_path}"
                )

            if snapshot_scraped_datetime_obj > master_scraped_datetime_obj:
                self.master_metadata["most_recent_scrape_date"] = snapshot_meta[
                    "date_scraped"
                ]
                logger.debug(
                    f"Updated master most_recent_scrape_date to {snapshot_date_scraped} from: {snapshot_meta_path}"
                )

                # Adds # of snapshot ids to # of total post IDs (allows for overcounting)
                num_aggregate_post_ids += snapshot_meta["num_all_post_ids"]

                # Update counts: compares current master & snapshot and takes the max
                latest_post_count: int = max(
                    self.master_metadata["num_unique_post_ids"],
                    snapshot_meta["num_all_post_ids"],
                )
                self.master_metadata["num_unique_post_ids"] = latest_post_count
                logger.debug(
                    f"Updated master num_unique_post_ids to {latest_post_count} from: {snapshot_meta_path}"
                )

                # Word count:
                latest_num_count: int = max(
                    self.master_metadata["num_aggregate_words"],
                    snapshot_meta["num_all_words"],
                )
                self.master_metadata["num_aggregate_words"] = latest_num_count
                logger.debug(
                    f"Updated master num_aggregate_words to {latest_num_count} from: {snapshot_meta_path}"
                )

            # Updates count after iterating through all snapshot metas
            self.master_metadata["num_aggregate_post_ids"] = num_aggregate_post_ids
            logger.debug(
                f"Updated master num_aggregate_post_ids to {num_aggregate_post_ids}"
            )

            self.master_metadata["num_lost_post_ids"] = num_lost_post_ids
            logger.debug(
                f"Updated master num_lost_post_ids to {num_lost_post_ids}"
            )

        #Convert sets to lists:
        self.master_metadata ["all_post_dates"] =  list(self.master_metadata ["all_post_dates"])
        self.master_metadata ["all_update_dates"] =  list(self.master_metadata ["all_update_dates"])
        self.master_metadata ["all_scrape_dates"] =  list(self.master_metadata ["all_scrape_dates"])
        self.master_metadata ["unique_post_ids"] =  list(self.master_metadata ["unique_post_ids"])
        self.master_metadata ["lost_post_ids"] =  list(self.master_metadata ["lost_post_ids"])

        return self.master_metadata
