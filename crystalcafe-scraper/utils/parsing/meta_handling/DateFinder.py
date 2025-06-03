from htmldate import find_date
import datetime

class DateFinder:
    def __init__(self, html):
        self.html = html

    def date_to_JSON(self) -> dict:
        """Captures date published, date updated, and date scraped from a specified website"""

        # Uses htmldate lib to find original and update dates
        publish_Date = find_date(
            self.html,
            extensive_search=True,
            original_date=True,
            outputformat="%Y-%m-%dT%H:%M:%S",
        )
        update_Date = find_date(
            self.html,
            extensive_search=False,
            original_date=False,
            outputformat="%Y-%m-%dT%H:%M:%S",
        )

        # Assumption is that each time this func is run during scrape, it will capture the time of scrape
        scrape_date = datetime.datetime.now()
        formatted_date = scrape_date.strftime("%Y-%m-%dT%H:%M:%S")

        dates = {
            "date_published": publish_Date,
            "date_updated": update_Date,
            "date_scraped": formatted_date,
        }

        return dates
