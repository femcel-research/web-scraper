import glob
import json
import os
import requests
import datetime
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from htmldate import find_date

#Utilities
from utils.scraping_handling import HomePageScraper
from .process_handling import HTMLCollector
from .process_handling import TextCollector
from .process_handling import MasterVersionGenerator
from .meta_handling  import MetaCollector



class Process:
    # TODO we are going to make the test file location a variable OR COMMAND LINE ARGUMENT!
    # TODO we are going to make the test file location a variable OR COMMAND LINE ARGUMENT!
    """Takes in a homepage URL then loops through the links on it, 'processing' each one"""

    # Path String Templates
    thread_meta_path = (
        "./data/crystal.cafe/{}/thread_meta_{}.json"  # Format with thread id, thread id
    )
    scan_meta_path = "{}/meta_{}.json"  # Format with folder_path, thread id
    thread_folder_path = "./data/crystal.cafe/{}"  # Format with thread id
    scan_folder_path = "./data/crystal.cafe/{}/{}"  # Format with thread id, scan_time

    successful_scans = 0

    def __init__(self, url):
        self.url = url
        self.scan_time = datetime.today().strftime("%Y-%m-%dT%H:%M:%S")

        log_dir = "./data/crystal.cafe/logs"
        os.makedirs(log_dir, exist_ok=True)
        log_filename = os.path.join(log_dir, f"{self.scan_time}.log")
      

        # Logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            filename= log_filename,
            filemode="w",
            format=(
                datetime.today().strftime("%Y-%m-%dT%H:%M:%S")
                + " %(levelname)s: %(message)s"
            ),  # TODO: Make str literal?
            style="%",
            level=logging.INFO,
        )

        page = requests.get(url, stream=True)

        try:
            # Get URLs
            self.scraper = HomePageScraper.HomePageScraper(url)
            self.url_list = self.scraper.urls_to_list()
        except:
            # If unable to scrape URLs due to homepage being down
            logging.info("Page is inaccessible.")
            logging.info(f"Status Code: {str(page.status_code)}")
        else:
            # If able to retrieve a url list, log message
            if len(self.url_list) <= 0:
                logging.critical("URL list is empty")
            else:
                logging.info("The following URLs have been scraped")
                for url in self.url_list:
                    logging.info(url)
                self.process_current_list()

    def log_processed_url(self, url):
        """Save list of processed URLs to txt file in data/processed"""
        with open("./data/crystal.cafe/processed/processed.txt", "a") as file:
            file.write(url + "\n")
        logging.info(f"Logging {url} in processed.txt")

    def make_soup_object(self, page):
        if type(page) == str:
            soup = BeautifulSoup(page, "html.parser")
            return soup
        else:
            soup = BeautifulSoup(page.content, "html.parser")
            return soup

    def process_html(self, url, html):
        # Meta and Content Scans are done via the local HTML file
        html_soup = self.make_soup_object(html)
        id = html_soup.find(class_="intro").get("id")

        # JSON current scan metadata file
        meta = MetaCollector(
            url,
            html,
            html_soup,
            self.scan_folder_path.format(id, self.scan_time),
            False,
        )
        (meta.meta_dump(False))
        logging.info(f"Saved current scan metadata for thread #{id}")

        # JSON current scan thread content file
        content = TextCollector(
            html_soup, self.scan_folder_path.format(id, self.scan_time)
        )
        thread_content = content.write_thread()
        logging.info(f"Saved current thread content for thread #{id}")

        # JSON thread scan metadata
        thread_meta = MetaCollector(
            url, html, html_soup, self.thread_folder_path.format(id), True
        )
        (thread_meta.meta_dump(True))
        logging.info(f"Saved/updated thread metadata for thread #{id}")

        # JSON master version file
        # TODO: probably a cleaner way to do this
        thread_meta_path = os.path.join(
            self.thread_folder_path.format(id), f"thread_meta_{id}.json"
        )
        with open(thread_meta_path, "r") as f:
            thread_meta = json.load(f)
        generator = MasterVersionGenerator(
            content.get_thread_contents(),
            thread_meta,
            id,
            self.thread_folder_path.format(id),
        )
        generator.write_master_thread()
        logging.info("Generated/updated master thread for thread #" + id)

    def make_scan_files(self, soup, url, id):
        logging.info(f"Starting new scan for thread #{id}")
        # JSON thread metadata file
        os.makedirs(
            self.scan_folder_path.format(id, self.scan_time), exist_ok=True
        )  # Make scan @ current time folder
        logging.info("Made folder for current scan")

        # HTML current scan file
        thread = HTMLCollector(soup, self.scan_folder_path.format(id, self.scan_time))
        (thread.saveHTML())
        logging.info(f"Saved HTML info for thread #{id}")
        thread_html = thread.getHTML()

        # Process the saved HTML
        self.process_html(url, thread_html)

        # Add URL to list of processed URLs
        self.log_processed_url(url)

        logging.info(f"Generated all scans for thread #{id}")  # Log message
        folder_path = self.scan_folder_path.format(id, self.scan_time)
        if os.path.exists(self.scan_meta_path.format(folder_path, id)):
            with open(self.scan_meta_path.format(folder_path, id)) as json_file:
                data = json.load(json_file)
                num_all_posts = str(data["num_all_posts"])
                num_new_posts = str(data["num_new_posts"])

                logging.info(f"{num_all_posts} posts scanned")
                logging.info(f"{num_new_posts} new posts scanned")

        self.successful_scans += 1

    def check_thread_folder(self, id):
        """Return True if a folder for the specified ID exists"""
        if os.path.exists(self.thread_folder_path.format(id)):
            logging.info(f"A thread folder exists for thread #{id}")
            return True
        else:
            logging.info(f"A thread folder does not exist for thread #{id}")
            return False

    def check_thread_meta(self, id):
        """Return True if an thread_meta file for the specified ID exists"""
        if os.path.exists(self.thread_meta_path.format(id, id)):
            logging.info(f"An thread_meta_{id}.json exists for thread #{id}")
            return True
        else:
            logging.info(f"An thread_meta_{id}.json does not exist for thread #{id}")
            return False

    def check_date_updated(self, page, id):
        """Return True if update_date in thread_meta matches current update_date"""
        with open(self.thread_meta_path.format(id, id)) as json_file:
            data = json.load(json_file)

        previous_update_date = datetime.strptime(
            data["date_updated"], "%Y-%m-%dT%H:%M:%S"
        )
        update_date = find_date(
            # Assigns update_date to the update date of page (the page being checked)
            page.content,
            extensive_search=False,
            original_date=False,
            outputformat="%Y-%m-%dT%H:%M:%S",
        )
        update_date = datetime.strptime(update_date, "%Y-%m-%dT%H:%M:%S")

        # Log message
        logging.info(f"Current update date for {id}: {str(update_date)}")
        logging.info(f"Previous update date for {id}: {str(previous_update_date)}")

        if update_date == previous_update_date:
            logging.info("update_dates match")  # Log message
            logging.info(f"The previous scan is up to date for thread #{id}")
            return True
        else:
            logging.info("update_dates do not match")  # Log message
            logging.info(f"The previous scan is not up to date for thread #{id}")
            return False

    def process_existing_files(self):
        """Processes existing files present within the crystal.cafe data subfolder."""
        directory = "./data/crystal.cafe"
        html_pattern = "*.html"  # Look for an html file
        meta_pattern = "meta_*.json"  # Look for a meta file
        
        logging.info("Processing existing threads")  # Log message
        for thread_folder in os.listdir(directory):
            thread_folder_path = os.path.join(directory, thread_folder)

            # If the thread folder is a directory, find its newest .html and meta file and use that to reprocess the thread.
            if os.path.isdir(thread_folder_path):
                html_search_path = os.path.join(thread_folder_path, "**", html_pattern)
                matching_html_files = glob.glob(html_search_path, recursive=True)

                meta_search_path = os.path.join(thread_folder_path, "**", meta_pattern)
                matching_meta_files = glob.glob(meta_search_path, recursive=True)

                # If the subfolder has an html file, process. Done to prevent processing of non-thread subfolders (i.e logs, processed, etc.)
                if len(matching_html_files) > 0:
                    newest_html = matching_html_files[len(matching_html_files) - 1]
                    newest_meta = matching_meta_files[len(matching_meta_files) - 1]
                    with open(newest_html, "r") as file:
                        html = file.read()

                    with open(newest_meta, "r") as file:
                        meta = json.load(file)

                    thread_url = meta["URL"]
                    html_soup = self.make_soup_object(html)
                    id = html_soup.find(class_="intro").get("id")
                    self.make_scan_files(html_soup, thread_url, id)

    def process_current_list(self):
        """For each URL in the list, get thread HTML, metadata JSON, and content JSON"""
        
        logging.info("Processing the URLs") 
        working_urls = 0
        failed_urls = 0
        
        for url in self.url_list:
            # Gets page from URL and makes a new directory for the thread
            logging.info(f"Processing {url}")  # Log message
            page = requests.get(url, stream=True)
            requests_soup = self.make_soup_object(page)
            intro_element = requests_soup.find(class_="intro")

            # Using intro_element since requests.get would still technically return a page, the page itself would just have a 404 error?
            # Tries to retrieve the id of the intro elem. If unable, it will log the specific status code of the page. Otherwise, continue as normal.
            # If at any point, a 404 slips through the cracks, retrieve code for stuff below committed prior to (11/19 6:15pm)
            try:
                id = intro_element.get("id")
            except:
                logging.warning(
                    f"{page.status_code} error; processing unsuccessful; skipping"
                )  # Log message
                failed_urls += 1
            else:
                working_urls += 1
                logging.info("Checking against previous scans")  # Log message
                if not self.check_thread_folder(
                    id
                ):  # return True if there is a thread ID folder
                    os.makedirs(
                        self.thread_folder_path.format(id), exist_ok=True
                    )  # if False, make thread ID folder
                    logging.info(f"Made thread folder for thread #{id}")
                if not self.check_thread_meta(
                    id
                ):  # return True if there is an thread_meta file for the thread
                    self.make_scan_files(requests_soup, url, id)
                else:
                    if not self.check_date_updated(
                        page, id
                    ):  # return True if previous scan up-to-date
                        self.make_scan_files(
                            requests_soup, url, id
                        )  # if False, then scan normally
            logging.info("Moving to next URL")

        logging.info("Fully processed all URLs; complete")  # Log message
        logging.info(
            f"Of the {str(len(self.url_list))} urls, {str(working_urls)} worked and {str(failed_urls)} did not"
        )
        logging.info(f"{str(self.successful_scans)} succesful scans were performed")
