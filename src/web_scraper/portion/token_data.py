import glob
from web_scraper.write_out import *
class TokenDataGenerator:
    def __init__(self, site_dir: str, list_of_thread_ids: list):
        """Looks through list of portion IDs, finds their master content JSONs and combines their post contents to one file."""
        self.list_of_thread_ids: list = list_of_thread_ids
        self.site_dir: str = site_dir

    def generate_portion_json(self) -> dict:
        content: dict = {}
        for id in self.list_of_thread_ids:
            thread_path: str = os.path.join(self.site_dir, id)
            master_content_search_path: str = os.path.join(thread_path, "master_version_*.json")
            master_content_files: str = glob.glob(master_content_search_path)
            if len(master_content_files) < 0:
                continue
            else: 
                master_content_path: str = master_content_files[0]
                with open(master_content_path, "r") as json_file:
                    master_content: dict = json.load(json_file)
            content.update({master_content["thread_id"]: self.grab_op_data(master_content)})
            content.update({master_content["thread_id"]: self.grab_replies_data(master_content)})
        return content
    
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
