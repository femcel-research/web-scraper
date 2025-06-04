class SoupError(Exception):
    """Exception raised for errors during BeautifulSoup initialization."""
    pass
 
class ContainerNotFoundError(Exception):
    """Exception raised when the specified container element is not found."""
    pass

class NoListItemsFoundError(Exception):
    """Exception raised when no elements found in specified container."""
    pass

class TagNotFoundError(Exception):
    """Exception raised when the specified HTML tag cannot be located."""
    pass

class NoThreadLinkFoundError(Exception):
    """Exception raised when no thread link can be found under an HTML tag."""