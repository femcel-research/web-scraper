class SiteStatHandler:
    def __init__(self, thread_meta_path: str, soup: BeautifulSoup):
        """Initializes with thread meta stats if it exists already; otherwise sets everything to 0"""
        self.soup = soup
        if os.path.exists(thread_meta_path):
            with open(thread_meta_path) as json_file:
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