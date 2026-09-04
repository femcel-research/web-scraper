# Imports
import json
import logging
import requests

logger = logging.getLogger(__name__)

def Fourchan_Fetcher(
    url: str,
) -> (
    dict
):  # we cant directly access the 4chan webpage due to cloudflare protections, so our best bet is using the 4chan api, which only returns info as a JSON
    """Fetches page content from a given 4chan URL and returns information as a JSON.

    Args:
        url (str): The URL that will be fetched.

    Returns:
        dict: page response as a JSON
    """
    try:
        logger.info(f"Fetching: {url}")
        _requests_session = requests.session()
        _requests_session.headers["User-Agent"] = "py-4chan/%s" % "0.6.0"
        response = _requests_session.get(url)
        content = json.loads(response.text)
        return content
    except requests.HTTPError as error:
        logger.error(f"HTTP error fetching {url}: {error}")
        raise OSError(f"HTTP error fetching {url}: {error}") from error
    except requests.RequestException as error:
        logger.error(f"Request error fetching {url}: {error}")
        raise OSError(f"Request error fetching {url}: {error}") from error
