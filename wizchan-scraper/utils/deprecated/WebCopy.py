import requests
import os
"""
DEPRECATED 20241024
"""

#pywebcopy is a crawler that works to save html, css, and .js from websites to local storage -Moyartu 
#install pywebcopy and lxml[html_clean] package for use.
from pywebcopy import save_webpage
from pywebcopy import Web

class Webcopy:
    def __init__(self, URL, threadNumber):
        self.URL = URL
        self.threadNumber = threadNumber

    def save_to_html(self):
        """Saves a copy of the URL to the HTML folder. Contents are nested in a folder named after the specific thread number."""
        
        save_webpage(
            url = self.URL,
        project_folder = './data/HTML',
        project_name = "thread_" + self.threadNumber,
        bypass_robots=True,
        debug=True,
        open_in_browser=False,
        delay=None,
        threaded = True #if set to false downloads will be incredibly slow.
        )