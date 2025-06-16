# Imports
import json
import os
import pytest

from web_scraper.parse.MasterMetaGenerator import MasterMetaGenerator

@pytest.fixture
def faux_content_dir(fs):
    """Custom fixture to create a fake data directory with snapshot files."""
    faux_thread_dir = "/faux_thread"
    snapshot_one = os.path.join(faux_thread_dir, "snapshot_1.json")
    snapshot_two = os.path.join(faux_thread_dir, "snapshot_2.json")
    snapshot_three = os.path.join(faux_thread_dir, "snapshot_3.json")

    # Create fake snapshot meta data
    board_name: str = "Test"
    thread_title: str = "Scraper"
    thread_id: str = "00"
    url: str = "example.com"
    date_published: str = "2025-06-16T10:00:01"
    # Snapshot One
    snapshot_one_date_updated: str = "2025-06-16T10:00:01"
    snapshot_one_date_scraped: str = "2025-06-16T10:00:02"
    snapshot_one_post_dates: list[str] = [
        "2025-06-16T10:00:01"]
    snapshot_one_post_ids: list[str] = [
        "00"]
    snapshot_one_num_post_ids: int = 1
    snapshot_one_num_words: int = 9
    # Snapshot Two
    snapshot_two_date_updated: str = "2025-06-16T10:00:02"
    snapshot_two_date_scraped: str = "2025-06-16T10:00:03"
    snapshot_two_post_dates: list[str] = [
        "2025-06-16T10:00:01", 
        "2025-06-16T10:00:02"]
    snapshot_two_post_ids: list[str] = [
        "00",
        "01"]
    snapshot_two_num_post_ids: int = 2
    snapshot_two_num_words: int = 16
    # Snapshot Three
    snapshot_three_date_updated: str = "2025-06-16T10:00:03"
    snapshot_three_date_scraped: str = "2025-06-16T10:00:04" 
    snapshot_three_post_dates: list[str] = [
        "2025-06-16T10:00:01", 
        "2025-06-16T10:00:02",
        "2025-06-16T10:00:03"]
    snapshot_three_post_ids: list[str] = [
        "00",
        "01",
        "02"]
    snapshot_three_num_post_ids: int = 3
    snapshot_three_num_words: int = 22
    
    snapshot_one_meta: dict = {
        "board_name":
            board_name,
        "thread_title":
            thread_title,
        "thread_id":
            thread_id,
        "url":
            url,
        "date_published":
            date_published,
        "date_updated":
            snapshot_one_date_updated,
        "date_scraped":
            snapshot_one_date_scraped,
        "all_post_dates":
            snapshot_one_post_dates,
        "all_post_ids": 
            snapshot_one_post_ids,
        "num_all_post_ids":
            snapshot_one_num_post_ids,
        "num_all_words":
            snapshot_one_num_words}
    # Needs to be bytes for fs.create_file()
    snapshot_one_bytes = json.dumps(snapshot_one_meta).encode('utf-8')

    snapshot_two_meta: dict = {
        "board_name":
            board_name,
        "thread_title":
            thread_title,
        "thread_id":
            thread_id,
        "url":
            url,
        "date_published":
            date_published,
        "date_updated":
            snapshot_two_date_updated,
        "date_scraped":
            snapshot_two_date_scraped,
        "all_post_dates":
            snapshot_two_post_dates,
        "all_post_ids": 
            snapshot_two_post_ids,
        "num_all_post_ids":
            snapshot_two_num_post_ids,
        "num_all_words":
            snapshot_two_num_words}
    snapshot_two_bytes = json.dumps(snapshot_two_meta).encode('utf-8')
    
    snapshot_three_meta: dict = {
        "board_name":
            board_name,
        "thread_title":
            thread_title,
        "thread_id":
            thread_id,
        "url":
            url,
        "date_published":
            date_published,
        "date_updated":
            snapshot_three_date_updated,
        "date_scraped":
            snapshot_three_date_scraped,
        "all_post_dates":
            snapshot_three_post_dates,
        "all_post_ids": 
            snapshot_three_post_ids,
        "num_all_post_ids":
            snapshot_three_num_post_ids,
        "num_all_words":
            snapshot_three_num_words}
    snapshot_three_bytes = json.dumps(snapshot_three_meta).encode('utf-8')

    # Create the fake directory and files
    fs.create_dir(faux_thread_dir)
    fs.create_file(snapshot_one, contents=snapshot_one_bytes)
    fs.create_file(snapshot_two, contents=snapshot_two_bytes)
    fs.create_file(snapshot_three, contents=snapshot_three_bytes)

    # Return the path to the created directory/files
    yield faux_thread_dir

def test_read_faux_data(faux_content_dir):
    """Test reading data from the faux directory created by the fixture."""
    # This is more of a test-internal test, to ensure the fixture is 
    # working properly

    # Arrange
    snapshot_1 = os.path.join(faux_content_dir, "snapshot_1.json")

    # Act & Assert
    assert os.path.exists(snapshot_1)

    with open(snapshot_1, "r", encoding="utf-8") as file:
        content = json.load(file)

    assert content["thread_id"] == "00"

def test__generate_master_meta(mocker, faux_content_dir):
    """Test _generate_master_meta() returns a correct master dict."""
    master_meta_generator = MasterMetaGenerator.__new__(
        MasterMetaGenerator)
    mocker.patch.object(MasterMetaGenerator, "__init__", return_value=None)

    # Create a list of meta file paths using faux directory
    snapshot_1 = os.path.join(faux_content_dir, "snapshot_1.json")
    snapshot_2 = os.path.join(faux_content_dir, "snapshot_2.json")
    snapshot_3 = os.path.join(faux_content_dir, "snapshot_3.json")
    paths = [snapshot_1, snapshot_2, snapshot_3]

    # Assign the empty variables that would normally by handled by init
    master_meta_generator.thread_id = ""
    master_meta_generator.master_metadata = {
        "board_name": "",
            "thread_title": "",
            "thread_id": "",
            "url": "",
            "date_published": "",
            "most_recent_update_date": "0001-01-01T00:00:00",
            "most_recent_scrape_date": "0001-01-01T00:00:00",
            "all_post_dates": set(),
            "all_update_dates": set(),
            "all_scrape_dates": set(),
            "snapshot_history": {},
            "num_aggregate_post_ids": 0,
            "unique_post_ids": set(),
            "num_unique_post_ids": 0,
            "lost_post_ids": set(),
            "num_aggregate_words": 0,
            "num_words_most_recent": 22}

    # Assign list of faux paths
    master_meta_generator.list_of_meta_paths = paths

    # Act & Assert
    master_meta = master_meta_generator._generate_master_meta()

    assert master_meta["url"] == "example.com"
    # TODO: Add more assertions