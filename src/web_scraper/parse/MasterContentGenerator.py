# Imports
import json
import logging
import os

logger = logging.getLogger(__name__)

class MasterContentGenerator:
    def __init__(self, content_paths: list[str]):
        """Generates a master content JSON according to content snapshots.

        Given a list of paths to snapshot content JSONs (gathered through 
        Glob), a master content JSON is generated and saved locally (after
        calling `content_dump()`).

        Args:
            content_paths (list[str]): Paths to snapshot content JSONs.

        Raises:
            Exception: A generic exception for unanticipated errors.
        """
        try:
            # Ensures at least one content path exists
            if len(content_paths) > 0:
                self.list_of_content_paths: list[str] = content_paths
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
                "thread_id": "",
                "original_post": self.original_post,
                "replies": self.all_replies,
            }
        except Exception as error:
            self.logging.error(f"Error when trying to initialize: {error}")
            raise Exception(f"Error when trying to initialize: {error}")

    def _generate_master_content(self) -> dict:
        """Converts snapshot content JSONs into single master content dict.
        
        Depends on a list of content paths having been set, as well as an
        OP dictionary, all_replies dictionary, all_post_ids set, and 
        master_contents dictionary having been initialized.
        """
        thread_id: str
        try:
            for i, snapshot_content_path in enumerate(
                self.list_of_content_paths):
                logger.debug(f"Snapshot path: {snapshot_content_path}")
                with open(snapshot_content_path, "r") as file:
                    data = json.load(file)
                snapshot_content = data
                # General board/thread info
                if i == 0:
                    thread_id: str = snapshot_content["thread_id"]
                    # except KeyError:
                        # thread_id: str = snapshot_content["thread_number"]

                    # I don't think we should handle this in this way
                    # because outdated snapshot content files should
                    # not be tolerated by the master generators (as
                    # important data may not be available)

                    # I think it would be better to have a descriptive
                    # error, so the problem can be resolved. Otherwise
                    # we will play a cat-and-mouse game, trying
                    # to supplement outdated data

                    self.master_contents.update({"thread_id": thread_id})
                # Retrieves OP and replies from snapshot and 
                # adds their ids to a set

                # try:
                original_post: dict = snapshot_content["original_post"]
                logger.debug(f"Original post retrieved.")
                # except KeyError:
                    # logger.warning(
                    #     f"Skipping snapshot {snapshot_content_path}:" 
                    #     " 'original_post' key not found.")
                    # continue

                # Here it also makes little sense to only handle KeyErrors
                # like this for a single key, when we could potentially
                # run into KeyErrors for the call below (if the passed
                # data is outdated)

                replies: dict = snapshot_content["replies"]
                logger.debug(f"Replies retrieved.")

                self._gather_all_post_ids(original_post, replies)
                logger.debug(f"All post ids gathered from snapshot.")

                # Update master posts with any new snapshot posts
                self.original_post.update(original_post)
                logger.debug(
                    f"Master original post updated to snapshot"
                    " original post.")

                self.all_replies.update(replies)
                logger.debug(f"Master replies updated with snapshot replies.")

            # original_post_id: str = self.original_post["post_id"]

            # Populates master thread content with data
            self.master_contents.update(
                {
                    "original_post": self.original_post,
                    "replies": self.all_replies,
                }
            )

            return self.master_contents
        
        except KeyError as error:
            logger.warning(
                f"KeyError ({error}) while generating master content from "
                f"list of paths: {self.list_of_content_paths}")
            logger.warning(
                "Check the data to ensure it follows formatting "
                "guidelines, and reparse if necessary")
            raise KeyError(
                f"KeyError ({error}) while generating master content from "
                f"list of paths: {self.list_of_content_paths}")
        except Exception as error:
            logger.error(f"Error when generating master: {error}")
            raise Exception(f"Error when generating master: {error}")

    def _gather_all_post_ids(self, original_post: dict, replies: dict):
        """Adds OP ID and all reply IDs into a set containing all post IDs.

        `self.all_post_ids` is updated using the passed dictionaries.

        Args:
            original_post (dict): Dictionary containing the original post.
            replies (dict): Dictionary containing all replies.
        """
        try:
            # Retrieves original post ID and adds to set of all post ids.
            original_post_id: str = original_post["post_id"]
            self.all_post_ids.add(original_post_id)
            logging.debug(
                f"Original post {original_post_id} has " 
                "been added to the master thread.")

            for reply in replies.values():
                # Retrieves reply ID and adds to set of all post ids.
                reply_id: str = reply.get("post_id")
                self.all_post_ids.add(reply_id)
                logging.debug(
                    f"Reply {reply_id} has been added to the master thread.")
        except Exception as error:
            logger.error(f"Error when gathering IDs: {error}")
            raise Exception(f"Error when gathering IDs: {error}")

    def content_dump(self) -> None:
        """Dumps master contents into a JSON file."""
        try:
            # Retrieves thread_id from OP post_id: done under the 
            # assumption OP post id = thread id.
            contents = self._generate_master_content()
            file_name = (
                f"master_version_{self.master_contents["thread_id"]}.json")

            # Finds thread directory by finding the parent of the snapshot folder
            snapshot_content_path = self.list_of_content_paths[0]
            snapshot_folder_path = os.path.dirname(snapshot_content_path)
            thread_folder_path = os.path.dirname(snapshot_folder_path)

            # File path of master content
            self.master_content_filepath = os.path.join(
                thread_folder_path, file_name)

            with open(
                self.master_content_filepath, "w", encoding="utf-8") as file:
                    json.dump(contents, file, indent=2, ensure_ascii=False)
        except Exception as error:
            logging.error(f"Error when dumping master content: {error}")
            raise Exception(f"Error when dumping master content: {error}")

    def get_path(self) -> str:
        """Currently unused."""
        return self.master_content_filepath
