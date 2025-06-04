# Imports
import logging
import requests

logger = logging.getLogger(__name__)

class NetworkError(Exception):
    """Exception raised for network-related errors during scraping."""
    pass

def fetch_html_content(url: str) -> bytes:
    """Fetches HTML content from a given URL.
    
    Args:
        url (str): The URL that will be fetched.
    """
    try:
        logger.info(f"Fetching: {url}")
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        logger.info(f"Successfully fetched: {url}")
        return response.content
    except requests.HTTPError as error:
        logger.error(f"HTTP error fetching {url}: {error}")
        raise NetworkError(f"HTTP error fetching {url}: {error}") from error
    except requests.RequestException as error:
        logger.error(f"Request error fetching {url}: {error}")
        raise NetworkError(f"Request error fetching {url}: {error}") from error
    

def archive_crawler(url:str) -> list[str]:
    """TODO: Given a starting URL, will crawl and collect overview pages.

    Starting from the provided overview page of a board on a
    compatible archive site, a list of URLs of other pages
    (not thread URLs, just other overview pages from which
    other threads can be accessed) are provided (including
    the original URL).

    Args:
        url (str): Starting overview page.

    Returns:
        list[str]: List of URLs of other overview pages.
    """
    # TODO: Implement