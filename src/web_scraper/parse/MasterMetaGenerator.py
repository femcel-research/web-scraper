from datetime import datetime
import json
import logging
import os


logger = logging.getLogger(__name__)


class MasterMetaGenerator:
    def __init__(self, meta_paths: list[str]):
        """Amalgamates snapshot meta JSONs for creation of a master meta JSON.
        
        Given a list of paths to snapshot meta JSONs (gathered through Glob), 
        a master metadata JSON is generated and saved locally.

        Args:
            meta_paths (list[str]): Filepaths to snapshot meta JSONs.
        """
        if len(meta_paths) > 0:
            self.meta_paths: list[str] = meta_paths
            logger.info("List of snapshot meta paths retrieved")
        else:
            logger.error("No snapshot meta paths found")
            raise IndexError("No snapshot meta paths found")

        self.snapshot_folder_path: str = os.path.dirname(meta_paths[0])
        self.thread_id: str = ""
        snapshot_history: dict = {} 

        all_post_dates: list = []
        all_update_dates: list = []
        all_scape_dates: list = []
        unique_post_ids: list = []
        lost_post_ids: list = []

        self.master_metadata: dict = {
            "board_name": "",
            "thread_title": "",
            "thread_id": "",
            "url": "",
            "date_published": "",
            "most_recent_update_date": "0001-01-01T00:00:00",
            "most_recent_scrape_date": "0001-01-01T00:00:00",
            "num_aggregate_post_ids": 0,
            "num_unique_post_ids": 0,
            "num_lost_post_ids": 0,
            "num_aggregate_words": 0,
            "num_words_most_recent": 0,
            "all_post_dates": all_post_dates,
            "all_update_dates": all_update_dates,
            "all_scrape_dates": all_scape_dates,
            "unique_post_ids": unique_post_ids,
            "lost_post_ids": lost_post_ids,
            "snapshot_history": snapshot_history}


    def master_meta_dump(self) -> None:
        """Dumps thread metadata into a JSON file.

        Args:
            metadata (dict): Dictionary containing metadata values.
            master_meta_filepath (str): Filepath for the master meta JSON.
        """
        # Pathing: Finds thread directory by finding parent folder 
        # of snapshot directory
        master_meta = self._generate_master_meta()
        thread_id = self.master_metadata["thread_id"]
        file_name = f"thread_meta_{thread_id}.json"
        thread_folder_path = os.path.dirname(self.snapshot_folder_path)
        self.master_meta_filepath = os.path.join(thread_folder_path, file_name)

        with open(self.master_meta_filepath, "w", encoding="utf-8") as f:
            json.dump(master_meta, f, indent=2, ensure_ascii=False)

        logger.info(
            f"Master metadata for thread {thread_id} has been updated")


    def _get_board_thread_info(self, snapshot_meta):
        """Gets board and thread information; only run once.
        
        Args:
            snapshot_meta (dict): Data from snapshot meta JSON file.
        """
        self.master_metadata["board_name"] = (
            snapshot_meta["board_name"])
        self.master_metadata["thread_title"] = (
            snapshot_meta["thread_title"])
        self.thread_id: str = (
            snapshot_meta["thread_id"])
        self.master_metadata["thread_id"] = (
            self.thread_id)
        self.master_metadata["url"] = (
            snapshot_meta["url"])
        self.master_metadata["date_published"] = (
            snapshot_meta["date_published"])
        logger.debug(
            "Updated board and thread information")


    def _update_snapshot_history(self, snapshot_meta, snapshot_path):
        """Gets snapshot post IDs and adds them to the snapshot history.
        
        The snapshot is looked at, and all of its post IDs are captured
        as a value, corresponding to the scrape date of the snapshot.

        Args:
            snapshot_meta (dict): Data from snapshot meta JSON file.
            snapshot_path (str): Path to snapshot meta JSON file.
        """
        date_scraped: str = snapshot_meta["date_scraped"]
        all_post_ids: list = snapshot_meta["all_post_ids"]
        self.master_metadata["snapshot_history"].update(
                {date_scraped: all_post_ids})
        logger.debug(
            "Updated master snapshot_history with "
            f"{ {date_scraped: all_post_ids}} from: "
            f"{snapshot_path}")


    def _update_date_sets(self, snapshot_meta, snapshot_path):
        """Updates master meta date sets.
        
        Updates `all_post_dates`, `all_update_dates`, and `all_scrape_dates`.

        Args:
            snapshot_meta (dict): Data from snapshot meta JSON file.
            snapshot_path (str): Path to snapshot meta JSON file.
        """
        all_post_dates: set = set(snapshot_meta["all_post_dates"])
        date_scraped: str = snapshot_meta["date_scraped"]
        date_updated: str = snapshot_meta["date_updated"]

        master_all_dates: set = set(self.master_metadata["all_post_dates"])
        master_all_dates.update(all_post_dates)
        self.master_metadata["all_post_dates"] = list(master_all_dates)
        self.master_metadata["all_scrape_dates"].append(date_scraped)
        self.master_metadata["all_update_dates"].append(date_updated)
        logger.debug(
            "Updated master meta data sets from: "
            f"{snapshot_path}")
        

    def _update_aggregate_words(self, snapshot_meta, snapshot_path):
        """Updates the count for aggregate words across all snapshots.
        
        Args:
            snapshot_meta (dict): Data from snapshot meta JSON file.
            snapshot_path (str): Path to snapshot meta JSON file.
        """
        num_all_words: int = int(snapshot_meta["num_all_words"])
        self.master_metadata["num_aggregate_words"] += num_all_words
        new_num_aggregate = self.master_metadata["num_aggregate_words"]
        logger.debug(
            "Updated master meta num_aggregate_words to "
            f"{new_num_aggregate} from: "
            f"{snapshot_path}")


    def _get_sorted_snapshot_dates(self) -> list:
        """Returns a list of sorted keys from `snapshot_history`.
        
        This can also act as a list of sorted dates from
        `all_scrape_dates` because every key is a scrape date.

        Depends on `self.master_metadata["snapshot_history"]` 
        having already been assigned keys and values.
        """
        snapshot_history: dict = self.master_metadata["snapshot_history"]
        format_string = "%Y-%m-%dT%H:%M:%S"
        sorted_dates: list = sorted(
            snapshot_history.keys(), 
            key=lambda x: datetime.strptime(
                x, 
                format_string))
        logger.debug(
            "Sorted date_scraped keys in snapshot history")
        return sorted_dates
    

    def _get_sorted_update_dates(self) -> list:
        """Returns a list of sorted dates from `all_update_dates`.
        
        Depends on `self.master_metadata["all_update_dates"]`
        having already been fully assigned.
        """
        update_dates: set = set(self.master_metadata["all_update_dates"])
        format_string = "%Y-%m-%dT%H:%M:%S"
        sorted_dates: list = list(
            sorted(
                update_dates, 
                key=lambda x: datetime.strptime(
                    x, 
                    format_string)))
        logger.debug(
            "Sorted all update dates")
        return sorted_dates
    

    def _get_most_recent_dates(self, sorted_update_dates, sorted_scrape_dates):
        """Gets the most recent update and scrape dates.
        
        Args:
            sorted_update_dates (list): Sorted list of update dates.
            sorted_scrape_dates (list): Sorted list of scrape dates.
        """
        most_recent_update = sorted_update_dates[-1]
        most_recent_scrape = sorted_scrape_dates[-1]
        # Assign most recent update date and scrape date
        self.master_metadata["most_recent_update_date"] = most_recent_update
        self.master_metadata["most_recent_scrape_date"] = most_recent_scrape
        logger.debug(
            "Got the most recent update and scrape dates: "
            f"{most_recent_update} and "
            f"{most_recent_scrape}")


    def _get_most_recent_num_words(
            self, sorted_snapshot_dates, words_per_scrape):
        """Gets the number of words in the most recent snapshot.
        
        Args:
            sorted_snapshot_dates (list): Sorted list of snapshot dates.
            words_per_scrape (dict): Dictionary of word counts per scrape.
        """
        most_recent_snapshot = sorted_snapshot_dates[-1]
        most_recent_num_words = words_per_scrape[most_recent_snapshot]
        self.master_metadata["num_words_most_recent"] = most_recent_num_words
        logger.debug(
            "Got the most recent number of words "
            f"{most_recent_num_words} from: "
            f"{most_recent_snapshot}")


    def _generate_master_meta(self) -> dict:
        """Amalgamates data from snapshot meta files to a master dictionary."""
        # Data based directly on snapshot metadata
        words_per_scrape: dict = {}

        for index, snapshot_meta_path in enumerate(self.meta_paths):
            # Using enumerate so static information doesn't need to be
            # assigned for every snapshot file
            with open(snapshot_meta_path, "r") as file:
                snapshot_meta = json.load(file)

            # Internal methods assign to self.master_metadata

            # General board/thread info assigned on one loop
            if index == 0:
                self._get_board_thread_info(snapshot_meta)

            # Gather information that is directly based on snapshot metadata
            # files here. Other data will be based solely on snapshot history
            self._update_snapshot_history(snapshot_meta, snapshot_meta_path)
            self._update_date_sets(snapshot_meta, snapshot_meta_path)
            self._update_aggregate_words(snapshot_meta, snapshot_meta_path)
            # Maintained so this can be accessed once the most recent
            # scrape date is calculated
            date_scraped = snapshot_meta["date_scraped"]
            num_all_words = snapshot_meta["num_all_words"]
            words_per_scrape.update({date_scraped: num_all_words})

        # Derived data
        sorted_update_dates: list = self._get_sorted_update_dates()
        sorted_snapshot_dates: list = self._get_sorted_snapshot_dates()
        # The snapshot history keys are all scrape dates, so it can also
        # be treated identically to a list of sorted scrape dates
        self._get_most_recent_dates(
            sorted_update_dates, 
            sorted_snapshot_dates)
        self._get_most_recent_num_words(
            sorted_snapshot_dates, 
            words_per_scrape)

        # Updated during iteration
        num_aggregate_post_ids: int = 0
        unique_post_ids: set = set()
        lost_post_ids: set = set()

        snapshot_history: dict = self.master_metadata["snapshot_history"]
        for snapshot_date in sorted_snapshot_dates:
            # Iterates in chronological order, from oldest to newest
            snapshot_post_ids: list = snapshot_history[snapshot_date]
            
            # Add to the count of IDs across all snapshots
            # (number of posts, including duplicates)
            num_aggregate_post_ids += len(snapshot_post_ids)
            
            # Check to see if there are any post IDs from previous
            # snapshots that should be in the current snapshot (if
            # they weren't removed)
            for post_id in unique_post_ids:
                if (post_id not in snapshot_post_ids and 
                    post_id not in lost_post_ids):
                    # Add any posts that were previously present,
                    # but aren't anymore
                    lost_post_ids.add(post_id)
                    
            # Update set of all post IDs
            unique_post_ids |= set(snapshot_post_ids)
        
        self.master_metadata["num_aggregate_post_ids"] = (
            num_aggregate_post_ids)
        self.master_metadata["unique_post_ids"] = list(
            unique_post_ids)
        self.master_metadata["num_unique_post_ids"] = len(
            unique_post_ids)
        self.master_metadata["lost_post_ids"] = list(
            lost_post_ids)
        self.master_metadata["num_lost_post_ids"] = len(
            lost_post_ids)
        
        
        logger.debug(
            "Successfully gathered master meta for "
            f"{self.master_metadata["thread_id"]}")

        return self.master_metadata