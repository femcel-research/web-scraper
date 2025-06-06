# Unique operations when compared to TagNotFoundError
class BoardNameAndTitleNotFoundError(Exception):
    """Exception raised when a board name/title is unable to be located."""
    pass

# Unique operations when compared to TagNotFoundError
class BoardNameAndTitleUnsupportedError(Exception):
    """Exception raised when we a board name/title is unable to be parsed."""
    pass

# Unique operations when compared to TagNotFoundError
class DateNotFoundError(Exception):
    """Exception raised when a date is not found from HTML data."""
    pass

class TagNotFoundError(Exception):
    """Exception raised when an tag/data is not found while using bs4 lib."""
    pass

class ContentInitError(Exception):
    """Exception raised when a snapshot content file is unable to be made."""
    pass