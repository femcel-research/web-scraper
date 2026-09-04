from web_scraper.utils.pathing_helpers import *
import json

def DataToJSON(
    data_dict: dict, scan_time_str: str, thread_id: str, name: str, siteName: str
):
    """Writes out dictionary of data for a thread snapshot to a JSON file.

    Files will be written to a JSON file according to the arguments passed:
    `f"{}/{thread_id}/{date_scraped}/{name}_{thread_id}.json"`

    Args:
        data_dict (dict): Data to be written out.
        date_scraped (str): Date scraped.
        thread_id (str): Thread number.
        name (str): The name ofstart_path the file (content, etc.)
        site_name (str): The site name for the data.
    """
    # TODO: Improve this method by adding tests and exception handling

    thread_path = getThreadPath(siteName, thread_id)
    thread_snapshot_path: str = getThreadSnapshotPath(thread_path, scan_time_str)
    makeDirectory(thread_snapshot_path)

    individual_file_path: str = os.path.join(thread_snapshot_path,f"{name}_{thread_id}.json")
    
    with open(individual_file_path, "w") as json_file:
        json.dump(data_dict, json_file, indent=4)