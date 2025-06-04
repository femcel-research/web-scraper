class ThreadIDNotFoundError(Exception):
    """Exception raised when a thread ID is unable to be located."""
    pass

class ContentInitError(Exception):
    """Exception raised when a snapshot content file is unable to be made."""
    pass