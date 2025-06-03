from bs4 import BeautifulSoup


class SoupHandling:
    """ A tool to handle the creation and management of a BeautifulSoup object.
    
    Attributes:
        page (str): output from a HTTP request.
    
    """
    def __init__(self, page: str):
       self.soup = BeautifulSoup(page, "html.parser")
    
    def get_soup(self) -> BeautifulSoup:
        """ Uses page inputted into handler to create and return a BeautifulSoup object.

        Returns: 
            BeautifulSoup: A BeautifulSoup object that can be manipulated via bs4 functions. 
        """
        return self.soup
    
    def soup_to_html(self) -> str:
        """
        Returns BeautifulSoup object as a string containing the website's HTML.

        Returns:
            str: String containing the HTML contents of the BeautifulSoup object
        """
        return str(self.soup)