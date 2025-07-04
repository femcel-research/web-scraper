import glob
from web_scraper.write_out import *
class TokenDataGenerator:
    def __init__(self, site_dir: str, list_of_thread_ids: list, token_data_path: str):
        """Looks through list of portion IDs, finds their master content JSONs and combines their post contents to one file."""
        self.list_of_thread_ids: list = list_of_thread_ids
        self.site_dir: str = site_dir
        self.token_data_path: str = token_data_path                        

    def generate_portion_json(self) -> dict:
        content: dict = {}
        final_content = {}
        for id in self.list_of_thread_ids:
            thread_path: str = os.path.join(self.site_dir, id)
            master_content_search_path: str = os.path.join(thread_path, "master_version_*.json")
            master_meta_search_path: str = os.path.join(thread_path, "thread_meta_*.json")
            master_content_files: str = glob.glob(master_content_search_path)
            master_meta_files: str = glob.glob(master_meta_search_path)
            if len(master_content_files) < 0 or len(master_meta_files) < 0:
                continue
            else: 
                master_content_path: str = master_content_files[0]
                master_meta_path: str = master_meta_files[0]

                # Opens master content
                with open(master_content_path, "r") as json_file:
                    master_content: dict = json.load(json_file)

                # Opens master meta
                with open(master_meta_path, "r") as json_file:
                    master_meta: dict = json.load(json_file)

            # The original code created a new dictionary for
            # every thread that was portioned out, then wouldn't
            # scrape from threads that were listed as having been
            # portioned out prior. Thus, board/thread key/value pairs
            # would constantly be overwritten, only allowing for
            # a single thread to be in a nested dictionary under a board.
            # This change is a messy (but hopefully temporary) fix intended
            # to fix this bug
            
            if os.path.exists(self.token_data_path):
                try:
                    with open(self.token_data_path, "r") as token_file:
                        data = json.load(token_file)
                        content = data[master_meta["board_name"]]
                except KeyError:
                    # No need to initialize if the board's never been
                    # given any thread keys
                    pass

            original_post: dict = self.grab_op_data(master_content)
            replies: dict = self.grab_replies_data(master_content)
            posts: dict = {}
            posts.update(original_post)
            posts.update(replies)
            content.update({master_content["thread_id"]:posts})
            final_content.update({master_meta["board_name"]: content})
        return final_content
    
    def grab_op_data(self, master_content) -> dict:
        op: dict = master_content["original_post"]
        return {op["post_id"]: op["post_content"]}
    
    def grab_replies_data(self, master_content) -> dict:
        replies_dict: dict = {}
        replies: dict = master_content["replies"]
        for reply in replies.values():
            reply: dict
            replies_dict.update({reply["post_id"]: reply["post_content"]})
        return replies_dict
