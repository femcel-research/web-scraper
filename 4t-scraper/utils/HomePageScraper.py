import time
from venv import logger
from htmldate import find_date
from bs4 import BeautifulSoup
import json
import requests
import datetime
import os


class HomePageScraper:
    """Makes a list of URLs from a homepage"""

    def __init__(self, url):
        """
        Initializes the HomePageScraper with a URL.

        Args:
            url (str): The URL of the homepage to scrape.
        """
        self.url = url
        self.url_list = []  # Corrected attribute name
        self.page = None  # added page

    def get_page_content(self, url):
        """
        Gets content of a given URL.

        Args:
            url (str): The URL to fetch.

        Returns:
            str: The content of the page, or None on error.
        """
        # https://requests.readthedocs.io/en/latest/user/quickstart/ Info on custom header:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        try:
            self.page = requests.get(url, stream=True, headers=headers)
            self.page.raise_for_status()
            return self.page.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def extract_links(self, soup, base_url):
        """
        Extracts all links from a BeautifulSoup object.

        Args:
            soup: parsed HTML
            base_url (str): The base URL of the site.

        Returns:
            list: A list of absolute URLs found on the page.
        """
        links = []
        for a_tag in soup.find_all("a"):
            href = a_tag.get("href")
            if href:
                # TODO: may be adding extra slashes in between links containing "boards.4chan.org" and "/page/#/"
                # as both of those cases contain double or triple slashes. Links are still accessible though.

                # handles relative URLs
                if href.startswith("/"):
                    link = base_url + href
                # handles absolute URLs
                elif href.startswith("http"):
                    link = href
                else:
                    # should add slash if relative URL does not have. could maybe use os.path? but once again this is a very temp solution.
                    link = base_url + href
                    if "/boards.4chan.org/lgbt/" in link:  # only get links w/ "/thread/"
                        link.strip("/boards.4chan.org/lgbt/")

                links.append(link)
        return links

    def crawl_site_for_links(self, start_page=1, max_page=1):
        """
        Crawls the archive site, starting from the specified page up until a max page number, and returns a list of all extracted links.

        Args:
            start_page (int, optional): The page number to start from, defaults to 1.

        Returns:
            list: A list of all unique URLs found on the archive pages. Returns an empty list on error.
        """
        page_number = start_page
        all_links = set()  # use a set to store unique links
        crawled_count = 0

        for page_number in range(start_page, max_page + 1):
            # construct the URL for the current page.
            if page_number == 1:
                page_url = self.url
            else:
                page_url = f"{self.url}page/{page_number}/"

            logger.info(f"Crawling page: {page_url}")
            content = self.get_page_content(page_url)
            if content:
                crawled_count += 1
                soup = BeautifulSoup(content, "html.parser")

                # link extraction
                links = self.extract_links(soup, page_url)
                for link in links:
                    if "/thread/" in link:  # only get links w/ "/thread/"
                        all_links.add(link)

                # to not overload server
                time.sleep(60)  # 1 minute delay

                page_number += 1
            else:
                logger.warning(
                    f"Failed to retrieve content from {page_url}.  Assuming this is the last page. Stopping."
                )
                break  # dont crawl if page doesn't load

        logger.info(f"Crawling complete.  Crawled {crawled_count} pages.")
        # log the total number of unique links
        logger.info(f"Found {len(all_links)} unique links.")
        return list(all_links)  # return the set of links as a list.

    def run(self):
        """
        Runs crawler and returns list of URLs.
        """
        return self.crawl_site_for_links()


# For CL-testing
if __name__ == "__main__":
    # Start the crawl.
    base_url = "https://archived.moe/lgbt/"
    crawler = HomePageScraper(base_url)
    archive_links = crawler.run()

    # Print the unique links found
    if archive_links:
        print("\nUnique Links Found:")
        for link in sorted(archive_links):
            print(link)
    else:
        print("No links found.")
