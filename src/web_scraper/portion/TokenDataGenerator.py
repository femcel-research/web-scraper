# Imports
import glob

from web_scraper.write_out import *

class TokenDataGenerator:
    """Given a list of portion IDs, post content is combined into JSONs."""

    def __init__(
            self, site_dir: str, thread_ids: list, 
            token_data_path: str, site_name: str):
        """Using the passed thread information, post content will be combined.
        
        Designed to be called once in the portioning process, not every time
        a thread is portioned.

        # TODO: Use thread log file for thread_ids

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


    def _combine_thread_content(self) -> dict:
        """Using a list of thread IDs, post content and data is combined.
        
        Returns:
            A dictionary of all posts from all threads listed in `thread_ids`.
        """
        final_content: dict = {}
        content: dict = {}

        for index, id in enumerate(self.thread_ids):
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

            original_post: dict = self._get_op_data(master_content)
            replies: dict = self._get_replies_data(master_content)
            posts: dict = {}
            posts.update(original_post)
            posts.update(replies)
            content.update({master_content["thread_id"]: posts})
            try:
                assert len(master_meta["unique_post_ids"]) == len(posts)
            except Exception as error:
                raise Exception(
                    "Inaccuracy when collecting posts for token data: "
                    f"{error}")
            # Final check to ensure accuracy
            final_content.update({master_meta["board_name"]: content})
        return final_content
    

    def _get_op_data(self, master_content: dict) -> dict:
        """Gets OP ID, date, and content.
        
        Args:
            master_content (dict): Thread's master content data.
        
        Returns:
            A dictionary with the OP ID as the single key.
        """
        op: dict = master_content["original_post"]
        return {
            op["post_id"]: {
                "date_posted": op["date_posted"],
                "content": op["post_content"]}}
    

    def _get_replies_data(self, master_content) -> dict:
        """Gets reply IDs, dates, and content.
        
        Args:
            master_content (dict): Thread's master content data.

        Returns:
            A dictionary with each reply ID as a key.
        """
        replies_dict: dict = {}
        replies: dict = master_content["replies"]
        for reply in replies.values():
            reply: dict
            replies_dict.update({
                reply["post_id"]: {
                    "date_posted": reply["date_posted"],
                    "content": reply["post_content"]}})
        return replies_dict

    
    def write_out_dict_to_jsons(self):
        """Generates (a) JSON file(s) containing all thread content data."""
        combined_thread_content: dict = self._combine_thread_content()

        # TODO: Add better handling for extra large files
        # file_index: int = 0
        # current_file_path = f"token_data_{file_index:03d}.json"
        # # Leading zeros: 001, 002, etc.
        # current_file = None
        # ...

        token_data_path: str = os.path.join(
            self.token_data_path, 
            f"{self.site_name}_token_data.json")

        with open(token_data_path, "w") as json_file:
            json.dump(combined_thread_content, json_file, indent=4)
