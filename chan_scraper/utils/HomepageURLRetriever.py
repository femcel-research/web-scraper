# Imports
import requests

from bs4 import BeautifulSoup

class HomepageURLRetriever:
    """A tool to retrieve a list of URLs that can iterated over. 

    Given a URL to a chan-style homepage, in which internal links are
    stored under the "box right" class, a list of URLs (with the appropriate
    domain name appended to the front) is returned.

    Attributes:
        page: The page retrieved from a URL.
        soup: A BeautifulSoup object; made from homepage.
        url_list: The list of URLs that will ultimately be returned.
        domain_param: The string that will be concatenated with relative URLs.
        container_param: Class URLs are stored in.
    """
    def __init__(self, url_param, domain_param, container_param):
        """Retrieves and returns a list of URLs.

        Args:
            url_param: URL to a chan-style homepage.
            domain_param: Domain prefix concatenated with relative URLs.
            container_param: Class URLs are stored in.
        """
        try:
            response = requests.get(url_param)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.content, "html.parser")
        except requests.HTTPError as error:
            # TODO: Print error in log
            pass
        self.url_list: list[str] = []
        self.domain_param: str = domain_param
        self.container_param: str = container_param

    def urls_to_list(self):
        """Returns a list of URLs.

        All URLs have he appropriate domain name appended to the front.
        
        Returns:
            url_list: List of URLs from the homepage. 
        """
        try:
            box_right = self.soup.find(class_=self.container_param)
            lists_box_right = box_right.find_all("li")
        except:  # TODO: Mention more explicit exception
            # TODO: Print error in log
            return None

        for list in lists_box_right:
            anchor_tag = list.find("a")
            if anchor_tag:
                # Get the value of "href" attribute; url info
                url = anchor_tag.get("href") 
                self.url_list.append(self.domain_param + url)

        return(self.url_list)