from glob import glob
import json
import os


class SiteMetaGenerator:

    def __init__(self, site_name):
        self.site_dir = os.path.join("./data",site_name)
        self.site_meta_file_path = os.path.join(site_dir,f"{site_name}_meta.json")
        master_meta_pattern = "**/thread_meta_*.json"
        search_pattern = os.path.join(site_dir, master_meta_pattern)
        self.list_of_master_metas: list[str] = glob.glob(search_pattern, recursive = True)

        self.masterdata = {
        "URL": "",
        "site_title": "",
        "description": "",
        "keywords": ""
        }
    
    def get_site_stats(self):
        """
        Returns a dictionary of site-wide statistics to be saved.
        """
        return {
            "num_sitewide_threads": self.num_sitewide_threads,
            "num_sitewide_total_posts": self.num_sitewide_total_posts,
            "num_sitewide_dist_posts": self.num_sitewide_dist_posts
        }
    
    

    

    def save_site_stats(self):
        """
        Saves the current site statistics to the specified file.
        """
        os.makedirs(os.path.dirname(self.site_meta_filepath), exist_ok=True)
        with open(self.site_meta_filepath, 'w') as json_file:
            json.dump(self.get_site_stats(), json_file, indent=4)