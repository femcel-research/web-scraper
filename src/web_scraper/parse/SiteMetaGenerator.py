import glob
import json
import os


class SiteMetaGenerator:

    def __init__(self, site_name):
        self.site_dir = os.path.join("./data", site_name)
        self.site_meta_file_path = os.path.join(self.site_dir, f"{site_name}_meta.json")
        master_meta_pattern = "**/thread_meta_*.json"
        search_pattern = os.path.join(self.site_dir, master_meta_pattern)
        self.list_of_master_metas: list[str] = glob.glob(search_pattern, recursive=True)

        url = ""
        if len(self.list_of_master_metas) > 0:
            first_found_meta_path = self.list_of_master_metas[0]
            with open(first_found_meta_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            first_found_meta = data
            url = first_found_meta["url"]

        self.masterdata = {
            "url": url,
            "site_title": site_name
            # "description": "", Unsure if we are using these. If so, TODO: will need to add description/keyword rtrieval in ChanScraper
            # "keywords": "",
        }

        

    def get_site_stats(self) -> dict:
        """
        Iterates through a list of master meta paths found in the site data subdirectory, and returns a dictionary of site-wide statistics to be dumped into a JSON.
        """
        num_sitewide_threads: int = len(
            self.list_of_master_metas
        )  # Assumption that number of sitewide threads should correlate with the number of master_thread metas found within a site's data subfolder.
        num_sitewide_total_posts: int = 0
        num_sitewide_dist_posts: int = 0

        #Updates values for num_sitewide_total_posts and num_sitewide_dist_posts
        for master_meta_path in self.list_of_master_metas:
            with open(master_meta_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            master_meta = data
            num_sitewide_total_posts += master_meta["num_aggregate_post_ids"]
            num_sitewide_dist_posts += master_meta["num_unique_post_ids"]

        return {
            "num_sitewide_threads": num_sitewide_threads,
            "num_sitewide_total_posts": num_sitewide_total_posts,
            "num_sitewide_dist_posts": num_sitewide_dist_posts,
        }

    def dump_site_meta(self):
        """
        Saves the current site statistics to the specified file.
        """
        stats: dict = self.get_site_stats()
        self.masterdata.update(stats)

        os.makedirs(os.path.dirname(self.site_meta_file_path), exist_ok=True)
        with open(self.site_meta_file_path, "w") as json_file:
            json.dump(self.masterdata, json_file, indent=2)
