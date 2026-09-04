from web_scraper.utils.pathing_helpers import *



def find_last_scrape_date(params: dict, scan_time_str) -> datetime:
    """
    Returns date of last scrape
    Args: 
        params: dictionary containing site parameters
    """
    params_data_dir = params["site_dir"]

    if not directoryExists(params_data_dir):
        makeDirectory(params_data_dir)
    
    subdirectories = subdirectorySearch(params_data_dir)
    if subdirectories:
        newest_subdirectory = getRecentSubdirectory(subdirectories)
        return modificationTimeToDatetime(getModificationTime(newest_subdirectory))

    else:
        # if there is no last scrape, set last scrape to time of current scrape
        return time_str_to_datetime(scan_time_str)

def time_str_to_datetime(time_str: str) -> datetime:
    return datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")