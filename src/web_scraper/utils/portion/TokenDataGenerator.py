# Imports
import glob

import jsonlines

from web_scraper.utils.write_out import *

class TokenDataGenerator:
    """Given a list of portion IDs, post content is combined into JSONLs."""

    def __init__(
            self, site_dir: str, thread_ids: list, 
            token_data_path: str, site_name: str):
        """Using the passed thread information, post content will be combined.
        
        Designed to be called once in the portioning process, not every time
        a thread is portioned.

        Args:
            site_dir (str): Dir where threads should be retrieved from.
            thread_ids (list): List of IDs which should be combined.  
            token_data_path (str): Path where JSON data should be written.
            site_name (str): Site name.
        """
        self.thread_ids: list = thread_ids
        self.site_dir: str = site_dir
        self.token_data_path: str = token_data_path
        self.site_name: str = site_name                        


    def _combine_thread_content(self) -> list:
        """Using a list of thread IDs, post content and data is combined.
        
        Returns a list of dictionaries (with each corresponding to a post) for
        efficient creation of a JSONL file.

        Returns:
            A list of all posts from all threads listed in `thread_ids`.
        """
        final_content: list = []

        post_counter: int        
        for id in self.thread_ids:
            post_counter = 0
            # Get the path for the thread directory
            thread_path: str = os.path.join(self.site_dir, id)
            # Get the paths for the master content and meta files
            master_content_search_path: str = os.path.join(
                thread_path, 
                "master_version_*.json")
            master_meta_search_path: str = os.path.join(
                thread_path, 
                "thread_meta_*.json")
            # The content file will provide the post IDs, content, and dates,
            # while the meta file will provide the board name
            master_content_files: str = glob.glob(master_content_search_path)
            master_meta_files: str = glob.glob(master_meta_search_path)

            if not master_content_files or not master_meta_files:
                # If there are no files
                continue
            else: 
                master_content_path: str = master_content_files[0]
                master_meta_path: str = master_meta_files[0]
                # There should only be one of each

                # Open master content
                with open(master_content_path, "r") as json_file:
                    master_content: dict = json.load(json_file)

                # Open master meta
                with open(master_meta_path, "r") as json_file:
                    master_meta: dict = json.load(json_file)

            op: dict = master_content["original_post"]
            
            original_post: dict = self._get_op_data(
                op, 
                master_meta)

            final_content.append(original_post)

            post_counter += 1

            replies: dict = master_content["replies"]
            for reply in replies.values():
                reply: dict
                reply_post: dict = self._get_reply_data(
                    reply,
                    master_meta)
                final_content.append(reply_post)

                post_counter += 1

            try:
                assert len(master_meta["unique_post_ids"]) == post_counter
            except Exception as error:
                raise Exception(
                    "Inaccuracy when collecting posts for token data: "
                    f"{error}")
            # Final check to ensure accuracy

        return final_content
    

    def _get_op_data(self, op: dict, master_meta: dict) -> dict:
        """Gets OP ID, date, board name, thread id, and content.
        
        Args:
            op (dict): OP data from a thread's master content data.
            master_meta (dict): Thread's master meta data.
        
        Returns:
            A dictionary with the OP post data.
        """
        return {
            "board_name": master_meta["board_name"],
            "thread_id": master_meta["thread_id"],
            "post_id": op["post_id"],
            "date_posted": op["date_posted"],
            "content": op["post_content"]}
    

    def _get_reply_data(self, reply: dict, master_meta: dict) -> dict:
        """Gets reply ID, date, board name. thread id, and content.
        
        Args:
            reply (dict): Reply data from a thread's master content data.
            master_meta (dict): Thread's master meta data.

        Returns:
            A dictionary with the reply post data.
        """
        return {
            "board_name": master_meta["board_name"],
            "thread_id": master_meta["thread_id"],
            "post_id": reply["post_id"],
            "date_posted": reply["date_posted"],
            "content": reply["post_content"]}

    
    def write_out_dict_to_jsonl(self):
        """Generates a JSONL file containing all thread content data."""
        combined_thread_content: list = self._combine_thread_content()

        token_data_path: str = os.path.join(
            self.token_data_path, 
            f"{self.site_name}_token_data.jsonl")

        with jsonlines.open(token_data_path, mode='w') as writer:
            writer.write_all(combined_thread_content)
