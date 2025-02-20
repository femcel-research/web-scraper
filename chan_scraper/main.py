# Imports
import datetime
import json

from .FullScrape import FullScrape
from .MetaScrape import MetaScrape
from .StatScrape import StatScrape


# TODO: 
# Let command-line arguments determine what kind of scan happens?
# Improve log structure

def load_param(filepath: str):
    """Loads parameters JSON file and returns JSON load for param access.
    
    Args:
        filepath: Location of parameters JSON file.
    """
    try:
        with open(filepath, "r") as params:
            return json.load(params)
    except FileNotFoundError:
        return None  # TODO: Print error in log
    except json.JSONDecodeError:
        return None  # TODO: Print error in log

if __name__ == "__main__":
    temp_param_path = ""  # TODO: Add actual path from command-line
    temp_url = ""  # TODO: Add actual homepage URL? Or take URL from params
    temp_html_directory = ""  # TODO: Add actual HTML directory
    temp_json_content_directory = ""  # TODO: Add actual JSON directory
    scan_time = datetime.today().strftime("%Y-%m-%dT%H:%M:%S") 
    # Load parameters JSON for use in other steps
    params = load_param(temp_param_path)  # TODO: Add actual param file
    if params is None:
        pass  # TODO: Print error in log and halt

    # TODO: Sort out different behavior; different scrape classes will
    # have different utils. Everything is designed to be fully modular
    if temp_param_path and temp_url:
        # Perform a "full scrape"
        FullScrape.full_scrape(params, temp_url, scan_time)
    elif temp_param_path and temp_html_directory:
        # Perform a "meta scrape" (placeholder)
        MetaScrape.meta_scrape(params, temp_html_directory, scan_time)
    elif temp_param_path and temp_json_content_directory:
        # Perform a "stat scrape" (placeholder)
        StatScrape.stat_scrape(params, temp_json_content_directory, scan_time)
    # Etc.