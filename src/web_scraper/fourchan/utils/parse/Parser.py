# general imports
from web_scraper.utils.parse.MasterTextGenerator import MasterTextGenerator
from web_scraper.utils.parse.MasterContentGenerator import MasterContentGenerator
from web_scraper.utils.parse.MasterMetaGenerator import MasterMetaGenerator
from web_scraper.utils.parse.SnapshotMetaGenerator import SnapshotMetaGenerator

from web_scraper.utils.write_out import *

from web_scraper.utils.pathing_helpers import *

#4chan specific
from web_scraper.fourchan.utils.board_scraper import BoardScraper
from web_scraper.fourchan.utils.board_to_content import BoardToContent
from web_scraper.fourchan.utils.parse.DataToJSON import DataToJSON
from web_scraper.fourchan.utils.fetch.Fourchan_Fetcher import Fourchan_Fetcher
from basc_py4chan import *

def Parser(params: dict, scan_time_str: str, last_scrape_time: datetime, thread: Thread, thread_id: str):
    """Performs processing on a given thread
    Args:
        params(dict): Dictionary containing board parameters
        scan_time_str(str): Time of scan
        thread (Thread): 4Chan thread
        thread_id (str): ID of thread"""
    
    # Param vars:
    site_name: str = params["site_name"]
    site_dir: str = params["site_dir"]

    # Pathing:
    thread_dir: str = getThreadPath(site_name, str(thread_id))
    thread_snapshot_path: str = getThreadSnapshotPath(thread_dir, scan_time_str)
    makeDirectory(thread_snapshot_path)
    content_file_path: str = getContentFilePath(thread_snapshot_path, thread_id)

    # create source JSON file
    makeSourceJSON(thread, scan_time_str, thread_id, site_name)

    # create content JSON file
    makeContentJSON(site_name, thread, thread_id, scan_time_str, last_scrape_time)   

    # Snapshot meta creation:
    makeContentMeta(content_file_path)

    # Master content creation:
    makeMasterContent(thread_dir)

    # Master text creation:
    makeMasterText(thread_dir, thread_id, site_dir)

    # Master meta creation:
    makeMasterMeta(thread_dir)

# Helper functions:

def makeSourceJSON(thread, scan_time_str, thread_id, site_name):
    # Saves API data as dict:
    api_data: dict = Fourchan_Fetcher(thread._api_url)
     
    # Saves source as a JSON
    DataToJSON(api_data, scan_time_str, thread_id, "source", site_name)
     
     
def makeContentJSON(site_name: str, thread: Thread, thread_id: str, scan_time_str: str, last_scrape_time: datetime):
     # Content JSON creation:
        content_parser: BoardToContent = BoardToContent(site_name, thread, scan_time_str, last_scrape_time)
    
        if content_parser.data is None:
            return #break out if older thread
    
        DataToJSON(
            content_parser.data, scan_time_str, thread_id, "content", site_name
        )

def makeContentMeta(content_file_path: str) -> dict:
    """
    Given a content file path, it creates a meta generator and dumps the respective content meta

    Args:
        content_file_path: string containing file path to content file
    
    Returns: 
        meta_dump: data contained in meta file
    """
    # TODO: Using the f-string for the data directory instead of
    # params["site_dir"] for now for testing

    # Snapshot meta creation:
    snapshot_meta_generator: SnapshotMetaGenerator = SnapshotMetaGenerator(
        content_file_path
    )
    return snapshot_meta_generator.meta_dump()

def makeMasterContent(thread_dir: str):
    # Master content creation:
    list_of_snapshot_contents: list[str] = getCandidateContentFiles(thread_dir)
    master_content_generator: MasterContentGenerator = MasterContentGenerator(
         list_of_snapshot_contents,
     )
    master_content_generator.content_dump()

def makeMasterText(thread_dir: str, thread_id: str, site_dir: str):
     master_text_generator: MasterTextGenerator = MasterTextGenerator(
         getMasterVersionPath(thread_dir, thread_id),
         site_dir,
     )
     master_text_generator.write_text() 

def makeMasterMeta(thread_dir: str):
     list_of_snapshot_metas: list[str] = getCandidateMetaFiles(thread_dir)
     master_meta_generator: MasterMetaGenerator = MasterMetaGenerator(
         list_of_snapshot_metas
     )
     master_meta_generator.master_meta_dump()