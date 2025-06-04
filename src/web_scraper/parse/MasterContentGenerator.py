import json
import logging


logger = logging.getLogger(__name__)


class MasterContentGenerator:
    def __init__(self, list_of_content_paths: list[str]):
        """
        Given a list of paths to snapshot content JSONs (gathered through Glob), a master content JSON is generated and saved locally.

        Args:
        list_of_content_paths (list[str]): List containing filepaths to snapshot content JSONs

        """

        if len(list_of_content_paths) > 0:
            self.list_of_content_paths: list[str] = list_of_content_paths
            logger.info("List of snapshot content paths retrieved.")
        else:
            logger.error("No snapshot content paths found.")
            raise IndexError("No snapshot content paths found.")

    def content_dump(self, content: dict, master_content_filepath: str) -> None:
        """Dumps thread contents into a JSON file.

        Args:
            content (dict): Dictionary containing thread data.
            master_content_filepath (str): String containing filepath for the master content JSON.
        """
        with open(master_content_filepath, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2, ensure_ascii=False)

    def snapshot_content_to_master_content(self):
        content: dict = {}
        thread_id: str = ""

        for snapshot_content_path in self.list_of_content_paths:
            with open(snapshot_content_path, "r") as file:
                data = json.load(file)
            snapshot_content = data