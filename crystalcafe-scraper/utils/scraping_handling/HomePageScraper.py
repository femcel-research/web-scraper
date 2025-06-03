from bs4 import BeautifulSoup
import requests

class HomePageScraper:
    """Makes a list of urls from homepage"""

    def __init__(self, url: str):
        self.url = url
        self.page = requests.get(url, stream=True)  
        self.soup = BeautifulSoup(self.page.content, "html.parser")
        self.url_list = []
               
    #TODO: abstract with params
    def urls_to_list(self) -> list[str]: 
        box_right = self.soup.find(class_="box right")
        lists_box_right = box_right.find_all("li")

        for list in lists_box_right:
            anchor_tag = list.find("a")
            if anchor_tag:
                url = anchor_tag.get("href")  # Get the value of "href" attribute; url info
                self.url_list.append("https://crystal.cafe" + url)

        return(self.url_list)