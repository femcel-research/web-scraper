# from datetime import datetime
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
        self.all_post_ids: set = set()

        # Populates master thread content with data
        self.master_contents = {
            # "date_of_previous_scan": "",
            # "date_of_latest_scan": "",
            "thread_id": "",
            "original_post": self.original_post,
            "replies": self.all_replies,
        }

    def generate_master_content(self) -> dict:
        """
        Converts all snapshot content JSONs into a single master content JSON.
        """
        thread_id: str
        for i, snapshot_content_path in enumerate(self.list_of_content_paths):
            logger.debug(f"Snapshot path: {snapshot_content_path}")
            with open(snapshot_content_path, "r") as file:
                data = json.load(file)
            snapshot_content = data
            # General board/thread info
            if i == 0:
                thread_id: str = snapshot_content["thread_id"]
                self.master_contents.update({"thread_id": thread_id})

            # Retrieves OP and replies from snapshot and adds their ids to a set
            try:
                original_post: dict = snapshot_content["original_post"]
                logger.debug(f"Original post retrieved.")
            except KeyError:
                logger.warning(
                    f"Skipping snapshot {snapshot_content_path}: 'original_post' key not found."
                )
                continue

            replies: dict = snapshot_content["replies"]
            logger.debug(f"Replies retrieved.")

            self.gather_all_post_ids(original_post, replies)
            logger.debug(f"All post ids gathered from snapshot.")

            # Update master posts with any new snapshot posts
            self.original_post.update(original_post)
            logger.debug(f"Master original post updated to snapshot original post.")

            self.all_replies.update(replies)
            logger.debug(f"Master replies updated with snapshot replies.")

        original_post_id: str = self.original_post["post_id"]

        # Populates master thread content with data
        self.master_contents.update(
            {
                "original_post": self.original_post,
                "replies": self.all_replies,
            }
        )

        return self.master_contents

    def gather_all_post_ids(self, original_post: dict, replies: dict):
        """Adds original post id and all reply ids into a set containing all post ids
        Args:
            original_post (dict): Dictionary containing the original post.
            replies (dict): Dictionary containing all replies."""

        # Retrieves original post ID and adds to set of all post ids.
        original_post_id: str = original_post["post_id"]
        self.all_post_ids.add(original_post_id)
        logging.debug(
            f"Original post {original_post_id} has been added to the master thread."
        )

        for reply in replies.values():
            # Retrieves reply ID and adds to set of all post ids.
            reply_id: str = reply.get("post_id")
            self.all_post_ids.add(reply_id)
            logging.debug(f"Reply {reply_id} has been added to the master thread.")

    def content_dump(self) -> None:
        """Dumps master contents into a JSON file.

        Args:
            content (dict): Dictionary containing content data.
            master_content_filepath (str): String containing filepath for the master meta JSON.
        """
        # Pathing: Finds thread directory by finding parent folder of snapshot directory

        # Retrieves thread_id from OP post_id: done under the assumption OP post id = thread id.
        contents = self.generate_master_content()
        file_name = f"master_version_{self.master_contents["thread_id"]}.json"

        # Finds thread directory by finding the parent of the snapshot folder
        snapshot_content_path = self.list_of_content_paths[0]
        snapshot_folder_path = os.path.dirname(snapshot_content_path)
        thread_folder_path = os.path.dirname(snapshot_folder_path)

        # File path of master content
        self.master_content_filepath = os.path.join(thread_folder_path, file_name)

        with open(self.master_content_filepath, "w", encoding="utf-8") as f:
            json.dump(contents, f, indent=2, ensure_ascii=False)

    def get_path(self) -> str:
        return self.master_content_filepath
