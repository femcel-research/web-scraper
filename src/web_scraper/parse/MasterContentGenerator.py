from datetime import datetime
import json
import logging
import os


logger = logging.getLogger(__name__)


class MasterContentGenerator:
    def __init__(self, list_of_content_paths: list[str]):
        """
        Given a list of paths to snapshot content JSONs (gathered through Glob), a master content JSON is generated and saved locally.

        Args:
        list_of_content_paths (list[str]): List containing filepaths to snapshot content JSONs

        """

        # Ensures at least one content path exists
        if len(list_of_content_paths) > 0:
            self.list_of_content_paths: list[str] = list_of_content_paths
            logger.info("List of snapshot content paths retrieved.")
        else:
            logger.error("No snapshot content paths found.")
            raise IndexError("No snapshot content paths found.")

        self.original_post: dict = {}
        self.all_replies: dict = {}

        # Establishes sets for all post ids and lost post ids
        self.all_post_ids: set = {}

    def snapshot_content_to_master(self) -> dict:
        """
        Converts all snapshot content JSONs into a single master content JSON.
        """

        master_contents: dict = {}
        snapshot_folder_path: str = ""

        for snapshot_content_path in self.list_of_content_paths:
            logger.info(f"Snapshot path: {snapshot_content_path}")
            with open(snapshot_content_path, "r") as file:
                data = json.load(file)
            snapshot_content = data

            # Retrieves OP and replies from snapshot and adds their ids to a set
            original_post: dict = snapshot_content["original_post"]
            logger.info(f"Original post retrieved.")

            replies: dict = snapshot_content["replies"]
            logger.info(f"Replies retrieved.")

            self.gather_all_post_ids(original_post, replies)
            logger.info(f"All post ids gathered from snapshot.")

            # Update master posts with any new snapshot posts
            self.original_post.update(original_post)
            logger.info(f"Master original post updated to snapshot original post.")

            self.all_replies.update(replies)
            logger.info(f"Master replies updated with snapshot replies.")

            snapshot_folder_path = os.path.dirname(snapshot_content_path)

        # Retrieves thread_id from OP post_id: done under the assumption OP post id = thread id.
        original_post_id: str = self.original_post["post_id"]

        # Pathing: Finds thread directory by finding parent folder of snapshot directory
        file_name = f"master_version{original_post_id}.json"
        thread_folder_path = os.path.dirname(snapshot_folder_path)
        content_file_path = os.path.join(thread_folder_path, file_name)

        # Populates master thread content with data
        master_contents = {
            "date_of_previous_scan": "",
            "date_of_latest_scan": "",
            "thread_id": original_post_id,
            "original_post": self.original_post,
            "replies": self.all_replies,
        }

        # Previous scan time is updated to the date of last scan
        previous_scan_time = master_contents["date_of_latest_scan"]
        master_contents.update({"date_of_previous_scan": previous_scan_time})
        logger.info(f"Date of previous scan has been updated to: {previous_scan_time}")

        # Date of latest scan is updated to current time
        current_time = datetime.today().strftime("%Y-%m-%dT%H:%M:%S")
        master_contents.update({"date_of_latest_scan": current_time})
        logger.info(f"Date of latest scan has been updated to: {current_time}")

        # Dumps contents into a locally saved JSON file
        self.content_dump(master_contents, content_file_path)

    def gather_all_post_ids(self, original_post: dict, replies: dict):
        """Adds original post id and all reply ids into a set containing all post ids
        Args:
            original_post (dict): Dictionary containing the original post.
            replies (dict): Dictionary containing all replies."""

        # Retrieves original post ID and adds to set of all post ids.
        original_post_id: str = original_post["post_id"]
        self.all_post_ids.add(original_post_id)
        logging.info(
            f"Original post {original_post_id} has been added to the master thread."
        )

        for reply in replies.values():
            # Retrieves reply ID and adds to set of all post ids.
            reply_id: str = reply.get("post_id")
            self.all_post_ids.add(reply_id)
            logging.info(f"Reply {reply_id} has been added to the master thread.")

    def content_dump(self, content: dict, master_content_filepath: str) -> None:
        """Dumps master contents into a JSON file.

        Args:
            content (dict): Dictionary containing content data.
            master_content_filepath (str): String containing filepath for the master meta JSON.
        """
        with open(master_content_filepath, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
