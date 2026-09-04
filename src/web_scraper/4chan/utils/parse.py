import glob
from web_scraper.utils.fetch.fetcher import fetch_fourchan_json_content
from scrape.board_scraper import BoardScraper
from web_scraper.utils.parse.MasterTextGenerator import MasterTextGenerator
from parse.HTMLToContent.BoardToContent import BoardToContent
from web_scraper.utils.parse.MasterContentGenerator import MasterContentGenerator
from web_scraper.utils.parse.MasterMetaGenerator import MasterMetaGenerator
from web_scraper.utils.parse.SnapshotMetaGenerator import SnapshotMetaGenerator
from web_scraper.utils.write_out import *

from basc_py4chan import *

def Parse(params: dict, scan_time_str: str, last_scrape: datetime, thread: Thread, thread_id: str):
    """Performs processing on a given thread
    Args:
        params(dict): Dictionary containing board parameters
        scan_time_str(str): Time of scan
        thread (Thread): 4Chan thread
        thread_id (str): ID of thread"""
    
    # Pathing:
    thread_dir: str = os.path.join(f"./data/{params["site_name"]}", str(thread_id))
    thread_snapshot_path: str = os.path.join(thread_dir, scan_time_str)
    os.makedirs(thread_snapshot_path, exist_ok=True)

    content_file_path: str = os.path.join(
        thread_snapshot_path, f"content_{thread_id}.json"
    )

    # Saves API data as dict:
    api_data: dict = fetch_fourchan_json_content(thread._api_url)
    snapshot_dict_to_json(
        api_data,
        scan_time_str,
        thread_id,
        "source",
        f"./data/{params["site_name"]}",
    )

    content_parser: BoardToContent = BoardToContent(
        params["site_dir"], thread, scan_time_str, last_scrape
    )

    if content_parser.data is None:
        return #break out if older thread

    # Content JSON creation:
    snapshot_dict_to_json(
        content_parser.data,
        scan_time_str,
        thread_id,
        "content",
        f"./data/{params["site_name"]}",
    )
    # TODO: Using the f-string for the data directory instead of
    # params["site_dir"] for now for testing

    # Snapshot meta creation:
    snapshot_meta_generator: SnapshotMetaGenerator = SnapshotMetaGenerator(
        content_file_path
    )
    snapshot_meta_generator.meta_dump()

    # Master content creation:
    candidate_content_files = os.path.join(thread_dir, "**", "content_*.json")
    list_of_snapshot_contents: list[str] = list(
        glob.glob(candidate_content_files, recursive=True)
    )
    master_content_generator: MasterContentGenerator = MasterContentGenerator(
        list_of_snapshot_contents,
    )
    master_content_generator.content_dump()

    # Master text creation:
    master_text_generator: MasterTextGenerator = MasterTextGenerator(
        os.path.join(
            thread_dir, f"master_version_{content_parser.data["thread_id"]}.json"
        ),
        params["site_dir"],
    )
    master_text_generator.write_text()

    # Master meta creation:
    candidate_meta_files = os.path.join(thread_dir, "**", "meta_*.json")
    list_of_snapshot_metas: list[str] = list(
        glob.glob(candidate_meta_files, recursive=True)
    )
    master_meta_generator: MasterMetaGenerator = MasterMetaGenerator(
        list_of_snapshot_metas
    )
    master_meta_generator.master_meta_dump()