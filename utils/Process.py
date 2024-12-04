import json
import os
import requests
import datetime
import logging
from bs4 import BeautifulSoup
from utils import HTMLCollector
from utils import MetaCollector
from utils import TextCollector
from utils import HomePageScraper
from datetime import datetime
from htmldate import find_date
from string import Template

class Process:
    """Takes in a homepage URL then loops through the links on it, 'processing' each one"""
    THREAD_META_PATH = Template("./data/$t/thread_meta_$t.json")  # $t for thread id
    SCAN_META_PATH = Template("$s/meta_$t.json")
    THREAD_FOLDER_PATH = Template("./data/$t")  # $t for thread id
    SCAN_FOLDER_PATH = Template("./data/$t/" + datetime.today().strftime("%Y-%m-%dT%H:%M:%S"))  # $t for thread id
    successful_scans = 0

    def __init__(self, url):
        # Logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            filename=("./data/logs/" + datetime.today().strftime('%Y-%m-%dT%H:%M:%S') + ".log"),
            filemode="w",
            format=(datetime.today().strftime('%Y-%m-%dT%H:%M:%S') + " %(levelname)s: %(message)s"),
            style="%",
            level=logging.INFO
        )
        
        page = requests.get(url, stream=True)
        
        try:
            # Get URLs
            self.scraper = HomePageScraper.HomePageScraper(url)
            self.url_list = self.scraper.urls_to_list()
        except:
            logging.info("Page is inaccessible.")
            logging.info("Status Code: " + str(page.status_code))
        else:   
            # Log message
            if (len(self.url_list) <= 0):
                logging.critical("URL list is empty")
            else: 
                logging.info("The following URLs have been scraped")
                for url in self.url_list:
                    logging.info(url)
                self.process_current_list()
                    
        

    def log_processed_url(self, url):
        """Save list of processed URLs to txt file in data/processed"""
        with open("./data/processed/processed.txt", "a") as file:
            file.write(url + '\n')
        logging.info("Logging " + url + " in processed.txt")

    def make_soup_object(self, page):
        if type(page) == str:
            soup = BeautifulSoup(page, "html.parser")
            return soup  
        else:
            soup = BeautifulSoup(page.content, "html.parser")
            return soup        
        
    def make_scan_files(self, soup, url, id):
        logging.info("Starting new scan for thread #" + id)
        # JSON thread metadata file
        os.makedirs(self.SCAN_FOLDER_PATH.substitute(t = id), exist_ok = True)  # Make scan @ current time folder
        logging.info("Made folder for current scan")

        # HTML current scan file
        thread = HTMLCollector(soup, self.SCAN_FOLDER_PATH.substitute(t = id))
        (thread.saveHTML())
        logging.info("Saved HTML info for thread #" + id)
        
        # Meta and Content Scans are done via the local HTML file
        thread_html = thread.getHTML()
        html_soup = self.make_soup_object(thread_html)

        # JSON current scan metadata file
        meta = MetaCollector(url, thread_html, html_soup, self.SCAN_FOLDER_PATH.substitute(t = id), False)
        (meta.meta_dump(False))
        logging.info("Saved current scan metadata for thread #" + id)

        # JSON current scan thread content file
        content = TextCollector(html_soup, self.SCAN_FOLDER_PATH.substitute(t = id))
        (content.write_thread())
        logging.info("Saved current thread content for thread #" + id)

        # JSON thread scan metadata
        thread_meta = MetaCollector(url, thread_html, html_soup, self.THREAD_FOLDER_PATH.substitute(t = id), True)
        (thread_meta.meta_dump(True))
        logging.info("Saved/updated thread metadata for thread #" + id)

        # Add URL to list of processed URLs
        self.log_processed_url(url)

        logging.info("Generated all scans for thread #" + id)  # Log message
        folder_path = self.SCAN_FOLDER_PATH.substitute(t = id)
        if os.path.exists(self.SCAN_META_PATH.substitute(s = folder_path, t = id)):
            with open(self.SCAN_META_PATH.substitute(s = folder_path, t = id)) as json_file:
                data = json.load(json_file)
                logging.info(str(data["num_all_posts"]) + " posts scanned")
                logging.info(str(data["num_new_posts"]) + " new posts scanned")

        self.successful_scans+=1

    def check_thread_folder(self, id):
        """Return True if a folder for the specified ID exists"""
        if(os.path.exists(self.THREAD_FOLDER_PATH.substitute(t = id))):
            logging.info("A thread folder exists for thread #" + id )
            return True
        else: 
            logging.info("A thread folder does not exist for thread #" + id)
            return False
        
    def check_thread_meta(self, id):
        """Return True if an thread_meta file for the specified ID exists"""
        if(os.path.exists(self.THREAD_META_PATH.substitute(t = id))):
           logging.info("An thread_meta_" + id + ".json exists for thread #" + id)
           return True
        else:
            logging.info("An thread_meta_" + id + ".json does not exist for thread #" + id)
            return False    
            

    def check_date_updated(self, page, id):
        """Return True if update_date in thread_meta matches current update_date"""
        with open(self.THREAD_META_PATH.substitute(t = id)) as json_file:
            data = json.load(json_file)
        
        previous_update_date = datetime.strptime(data["date_updated"], "%Y-%m-%dT%H:%M:%S")
        update_date = find_date(
            # Assigns update_date to the update date of page (the page being checked)
            page.content,
            extensive_search=False,
            original_date=False,
            outputformat="%Y-%m-%dT%H:%M:%S",
        )
        update_date = datetime.strptime(update_date, "%Y-%m-%dT%H:%M:%S")

        # Log message
        logging.info("Current update date for " + id + ": " + str(update_date))
        logging.info("Previous update date for " + id + ": " + str(previous_update_date))

        if update_date == previous_update_date:
            logging.info("update_dates match")  # Log message
            logging.info("The previous scan is up to date for thread #" + id)
            return True
        else:
            logging.info("update_dates do not match")  # Log message
            logging.info("The previous scan is not up to date for thread #" + id)
            return False

    def process_current_list(self):
        """For each URL in the list, get thread HTML, metadata JSON, and content JSON"""
        
        
        logging.info("Processing the URLs")  # Log message
        working_urls = 0
        failed_urls = 0

        for url in self.url_list:
            # Gets page from URL and makes a new directory for the thread
            logging.info("Processing " + url)  # Log message
            page = requests.get(url, stream=True)  
            requests_soup = self.make_soup_object(page)
            intro_element = requests_soup.find(class_="intro")
            
            # Using intro_element since requests.get would still technically return a page, the page itself would just have a 404 error?
            # Tries to retrieve the id of the intro elem. If unable, it will log the specific status code of the page. Otherwise, continue as normal.
            # If at any point, a 404 slips through the cracks, retrieve code for stuff below committed prior to (11/19 6:15pm)
            try:
               id = intro_element.get("id") 
            except:
                logging.warning(page.status_code + " error; processing unsuccessful; skipping")  # Log message
                failed_urls+=1
            else:
                working_urls+=1
                logging.info("Checking against previous scans")  # Log message
                if not self.check_thread_folder(id):  # return True if there is a thread ID folder
                    os.makedirs(self.THREAD_FOLDER_PATH.substitute(t = id), exist_ok=True)  # if False, make thread ID folder
                    logging.info("Made thread folder for thread #" + id)
                if not self.check_thread_meta(id):  # return True if there is an thread_meta file for the thread
                    self.make_scan_files(requests_soup, url, id)
                else: 
                    if not self.check_date_updated(page, id):  # return True if previous scan up-to-date
                        self.make_scan_files(page, requests_soup, url, id)  # if False, then scan normally
            logging.info("Moving to next URL")
                            
        logging.info("Fully processed all URLs; complete") # Log message
        logging.info("Of the " + str(len(self.url_list)) + " urls, " + str(working_urls) + " worked and " + str(failed_urls) + " did not")
        logging.info(str(self.successful_scans) + " succesful scans were performed")

                    


            