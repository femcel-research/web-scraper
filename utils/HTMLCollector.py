from requests_html import HTMLSession
from bs4 import BeautifulSoup
import os


#TODO no longer need to pass page
class HTMLCollector:
    """Saves a URL's HTML into a file"""
    def __init__(self, soup, folder_path):
        self.soup = soup
        self.folder_path = folder_path
        
        self.threadNumber = self.soup.find(class_="intro").get("id")
        self.file_name = "thread_" + self.threadNumber + ".html"
        self.file_path = os.path.join(self.folder_path, self.file_name) 

    def saveHTML(self):
        """Saves HTML"""
        #soup = BeautifulSoup(self.page.content, "html.parser")
        # Should hopefully always return the thread number, given that for crystal.cafe, the thread number is always the first id in the intro class

        # moved to init:
        #   threadNumber = self.soup.find(class_="intro").get("id")
        #   file_name = "thread_" + threadNumber + ".html"
        #   file_path = os.path.join(self.folder_path, file_name) 
             
        with open(self.file_path, "w") as f:
            f.write(self.soup.prettify())
    
    def getHTML(self):
        file_path = os.path.join(self.folder_path, self.file_name) 
        with open(file_path, "r") as f:
            html_content = f.read()
        return html_content
            