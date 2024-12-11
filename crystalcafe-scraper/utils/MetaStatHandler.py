import json
import os


class MetaStatHandler:
    def __init__(self, thread_meta):
        """Initializes with thread meta stats if it exists already; otherwise sets everything to 0"""
        if os.path.exists(thread_meta):
            with open(thread_meta) as json_file:
                self.data = json.load(json_file)

            self.dist_post_ids = self.data["dist_post_ids"]  # []; all distinctive post_ids across all scans
            self.lost_post_ids = self.data["lost_post_ids"]  # []; everytime a post is in dist_post_ids but not all_post_ids && not in lost_post_ids already, add here
            self.num_dist_posts = self.data["num_dist_posts"] # += w/ num_new_posts
            self.num_total_posts = self.data["num_total_posts"]  # Posts across all scans; += w/ num_all_posts    
            self.num_lost_posts = self.data["num_lost_posts"]  # Posts that formerly appeared, but did not in current scan
        else: 
            self.dist_post_ids = []
            self.lost_post_ids = []
            self.num_dist_posts = 0 
            self.num_total_posts = 0 
            self.num_lost_posts = 0 

    def set_scan_and_thread_values(self, soup):
        """Sets the values for the current scan of the website and changes thread meta file values from initialized values
        accordingly"""
        # Get a masterlist of all posts
        self.all_post_ids = []
        original_post = soup.find(class_="post op")
        self.all_post_ids.append(original_post.find(class_="intro").get("id"))

        for reply in soup.find_all(class_="post reply"):
            self.all_post_ids.append(reply.find(class_="intro").get("id"))

        # Get the title of the website for any use in update_site_meta()
        meta_keywords = soup.find("meta", attrs={"name": "keywords"})
        if meta_keywords:
            keywords = meta_keywords["content"]
        else:
            keywords = ""
        self.site_title = keywords.split(",")[0]
    
        self.new_post_ids = []
        self.new_lost_posts = []
        self.num_new_lost_posts = 0

        # Make a list of all post_ids that aren't already in dist_post_ids in thread meta file
        for post_id in self.all_post_ids:
            if post_id not in self.dist_post_ids:
                self.new_post_ids.append(post_id)
                self.dist_post_ids.append(post_id)
        
        # Make a list/tally the post_ids that were once added to dist_post_ids, but aren't in the current scan
        for post_id in self.dist_post_ids:
            if post_id not in self.all_post_ids and post_id not in self.lost_post_ids: 
                self.new_lost_posts.append(post_id)
                self.lost_post_ids.append(post_id)
                self.num_new_lost_posts += 1

        self.num_all_posts = len(self.all_post_ids)
        self.num_new_posts = len(self.new_post_ids)
        self.num_dist_posts += self.num_new_posts
        self.num_total_posts += self.num_all_posts
        self.num_lost_posts += self.num_new_lost_posts
    
    def set_site_values(self, site_data, new_thread):
        """If there is a site meta file already, it'll grab the appropriate values then update them using new numbers
        retrieved from set_scan_and_thread_values(); else set them to 0. If new_thread, num_sitewide_threads += 1"""
        if "num_sitewide_threads" in site_data:
            self.num_sitewide_threads = site_data["num_sitewide_threads"]
            self.num_sitewide_total_posts = site_data["num_sitewide_total_posts"]
            self.num_sitewide_dist_posts = site_data["num_sitewide_dist_posts"]

        else: 
            self.num_sitewide_threads = 0
            self.num_sitewide_total_posts = 0
            self.num_sitewide_dist_posts = 0
        
        if new_thread:
            self.num_sitewide_threads += 1  

        self.num_sitewide_total_posts += self.num_all_posts
        self.num_sitewide_dist_posts += self.num_dist_posts

    def get_thread_meta(self):
        """Returns a dictionary for a JSON file of dist_post_ids, lost_post_ids, num_dist_posts
        num_total_posts, num_lost_posts"""
        return {
            "dist_post_ids" : self.dist_post_ids,
            "lost_post_ids" : self.lost_post_ids,
            "num_dist_posts" : self.num_dist_posts,
            "num_total_posts" : self.num_total_posts,
            "num_lost_posts" : self.num_lost_posts
        }
    
    def get_scan_meta(self):
        """Returns a dictionary for a JSON file of all_post_ids, new_post_ids, new_lost_posts
        num_all_posts, num_new_posts, num_new_lost_posts"""
        return {
            "all_post_ids" : self.all_post_ids,
            "new_post_ids" : self.new_post_ids,
            "new_lost_posts" : self.new_lost_posts,
            "num_all_posts" : self.num_all_posts,
            "num_new_posts" : self.num_new_posts,
            "num_new_lost_posts" : self.num_new_lost_posts
        }
    
    def get_site_meta(self):
        """Returns a dictionary for a JSON file of num_sitewide_threads, num_sitewide_total_posts, num_sitewide_dist_posts"""
        return {
            "num_sitewide_threads" : self.num_sitewide_threads,
            "num_sitewide_total_posts" : self.num_sitewide_total_posts,
            "num_sitewide_dist_posts" : self.num_sitewide_dist_posts
        }
    
    def update_site_meta(self, new_thread):
        """Call after setting scan and thread values; accesses and updates site meta file with appropriate stats from
        get_site_meta()"""
        site_meta = "./data/" + self.site_title + "_meta.json"

        with open(site_meta, 'r+') as site_json_file:
            site_data = json.load(site_json_file)
            self.set_site_values(site_data, new_thread)
            # Update existing values and add new ones
            site_data.update(self.get_site_meta())
            site_json_file.seek(0)
            json.dump(site_data, site_json_file, indent=4)
            site_json_file.truncate()
