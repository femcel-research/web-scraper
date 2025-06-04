class BoardNameAndTitleNotFoundError(Exception):
    """Exception raised when a board name/title is unable to be located."""
    pass

class BoardNameAndTitleUnsupportedError(Exception):
    """Exception raised when we a board name/title is unable to be parsed."""
    pass

class ThreadIDNotFoundError(Exception):
    """Exception raised when a thread ID is unable to be located."""
    pass

class DateNotFoundError(Exception):
    """Exception raised when a date is not found from HTML data."""

class ContentInitError(Exception):
    """Exception raised when a snapshot content file is unable to be made."""
    pass