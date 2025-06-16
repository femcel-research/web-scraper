# Imports
import json
import os
import pytest

from web_scraper.parse.MasterContentGenerator import MasterContentGenerator

@pytest.fixture
def faux_content_dir(fs):
    """Custom fixture to create a fake data directory with snapshot files."""
    faux_thread_dir = "/faux_thread"
    snapshot_one = os.path.join(faux_thread_dir, "snapshot_01.json")
    snapshot_two = os.path.join(faux_thread_dir, "snapshot_02.json")
    snapshot_three = os.path.join(faux_thread_dir, "snapshot_03.json")
    snapshot_four = os.path.join(faux_thread_dir, "snapshot_04.json")
    # Evil depricated snapshot for testing interactions with outdated files
    snapshot_depr = os.path.join(faux_content_dir, "snapshot_depr.json")

    # Create fake snapshot content data
    # (Likely don't need all of this for testing, but I would rather be
    # safe and be able to repurpose this fixture for other tests)
    board_name: str = "Test"
    thread_title: str = "Scraper"
    thread_id: str = "00"
    url: str = "example.com"
    date_published: str = "2025-06-16T10:00:01"
    date_updated: str = "2025-06-16T10:00:03"
    date_scraped: str = "2025-06-16T10:00:04"
    original_post: dict = {
        "date_posted":
            "2025-06-16T10:00:01",
        "post_id": 
            "00",
        "post_content":
            "The quick brown fox jumps over the lazy dog.",
        "img_links": 
            ["ex.com/b/t/11.jpg"],
        "username":
            "Dorothy Ashby",
        "replied_to_ids":
            ["/b/01"]}    
    first_reply: dict = {
        "date_posted":
            "2025-06-16T10:00:02",
        "post_id": 
            "01",
        "post_content":
            "Sphinx of black quartz judge my vow.",
        "img_links": 
            [],
        "username":
            "Alice Coltrane",
        "replied_to_ids":
            []}
    second_reply: dict = {
        "date_posted":
            "2025-06-16T10:00:03",
        "post_id": 
            "02",
        "post_content":
            "The five boxing wizards jump quickly.",
        "img_links": 
            ["ex.com/b/t/100.jpg"],
        "username":
            "Brandee Younger",
        "replied_to_ids":
            []}
    third_reply: dict = {
        "date_posted":
            "2025-06-16T10:00:03",
        "post_id": 
            "03",
        "post_content":
            "Heavy boxes perform quick waltzes and jigs.",
        "img_links": 
            [],
        "username":
            "Casper Reardon",
        "replied_to_ids":
            ["02"]}

    empty_replies: dict = {}
    one_reply: dict = {
        "reply_01": first_reply}
    two_replies: dict = {
        "reply_01": first_reply, "reply_02": second_reply}
    two_replies_one_lost: dict = {
        "reply_01": first_reply, "reply_03": third_reply}
    
    snapshot_one_content: dict = {
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
            date_updated,
        "date_scraped":
            date_scraped,
        "original_post":
            original_post,
        "replies": empty_replies}
    # Needs to be bytes for fs.create_file()
    snapshot_one_bytes = json.dumps(snapshot_one_content).encode('utf-8')

    snapshot_two_content: dict = {
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
            date_updated,
        "date_scraped":
            date_scraped,
        "original_post":
            original_post,
        "replies": one_reply}
    snapshot_two_bytes = json.dumps(snapshot_two_content).encode('utf-8')
    
    snapshot_three_content: dict = {
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
            date_updated,
        "date_scraped":
            date_scraped,
        "original_post":
            original_post,
        "replies": two_replies}
    snapshot_three_bytes = json.dumps(snapshot_three_content).encode('utf-8')

    snapshot_four_content: dict = {
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
            date_updated,
        "date_scraped":
            date_scraped,
        "original_post":
            original_post,
        "replies": two_replies_one_lost}
    snapshot_four_bytes = json.dumps(snapshot_four_content).encode('utf-8')

    snapshot_depr_content: dict = {
        "thread_number": "00",
        "original_post": {
            "post_id": "00",
            "username": "Dorothy Ashby",
            "reply_to_another_thread?": False,
            "date_posted": "2025-06-16T10:00:01",
            "image_links": [],
            "post_content": "The quick brown fox jumps over the lazy dog.",
            "replied_thread_ids": []},
        "replies": {
            "reply_01": {
                "post_id": "01",
                "ids_of_replied_posts": [],
                "username": "Alice Coltrane",
                "date_posted": "2025-06-16T10:00:02",
                "image_links": [],
                "post_content": "Sphinx of black quartz judge my vow."}}}
    snapshot_depr_bytes = json.dumps(snapshot_depr_content).encode('utf-8')

    # Create the fake directory and files
    fs.create_dir(faux_thread_dir)
    fs.create_file(snapshot_one, contents=snapshot_one_bytes)
    fs.create_file(snapshot_two, contents=snapshot_two_bytes)
    fs.create_file(snapshot_three, contents=snapshot_three_bytes)
    fs.create_file(snapshot_four, contents=snapshot_four_bytes)
    fs.create_file(snapshot_depr, contents=snapshot_depr_bytes)

    # Return the path to the created directory/files
    yield faux_thread_dir

def test_read_faux_data(faux_content_dir):
    """Test reading data from the faux directory created by the fixture."""
    # This is more of a test-internal test, to ensure the fixture is 
    # working properly

    # Arrange
    snapshot_one = os.path.join(faux_content_dir, "snapshot_01.json")

    # Act & Assert
    assert os.path.exists(snapshot_one)

    with open(snapshot_one, "r", encoding="utf-8") as file:
        content = json.load(file)

    assert content["thread_id"] == "00"

def test__generate_master_content(mocker, faux_content_dir):
    """Test _generate_master_content() returns a correct master dict."""
    # Arrange
    master_content_generator = MasterContentGenerator.__new__(
        MasterContentGenerator)
    mocker.patch.object(MasterContentGenerator,"__init__", return_value=None)

    # Create a list of content file paths using faux directory
    snapshot_one = os.path.join(faux_content_dir, "snapshot_01.json")
    snapshot_two = os.path.join(faux_content_dir, "snapshot_02.json")
    snapshot_three = os.path.join(faux_content_dir, "snapshot_03.json")
    paths = [snapshot_one, snapshot_two, snapshot_three]

    # Assign the empty variables that would normally be handled by init
    master_content_generator.original_post = {}
    master_content_generator.all_replies = {}
    master_content_generator.all_post_ids = set()
    master_content_generator.master_contents = {
        "thread_id": "",
        "original_post": master_content_generator.original_post,
        "replies": master_content_generator.all_replies}
    
    # Assign list of faux paths
    master_content_generator.list_of_content_paths = paths

    # Act & Assert
    master_contents = master_content_generator._generate_master_content()
    
    # Various data points
    assert master_contents["thread_id"] == "00"

    assert master_contents["original_post"]["replied_to_ids"] == (
        ["/b/01"])

    # The method looked at multiple files
    assert master_contents["replies"]["reply_02"] == {
        "date_posted":
            "2025-06-16T10:00:03",
        "post_id": 
            "02",
        "post_content":
            "The five boxing wizards jump quickly.",
        "img_links": 
            ["ex.com/b/t/100.jpg"],
        "username":
            "Brandee Younger",
        "replied_to_ids":
            []}
    
def test__generate_master_content_one_lost(mocker, faux_content_dir):
    """Test _generate_master_content() returns a correct master dict."""
    # Arrange
    master_content_generator = MasterContentGenerator.__new__(
        MasterContentGenerator)
    mocker.patch.object(MasterContentGenerator,"__init__", return_value=None)

    # Create a list of content file paths using faux directory
    snapshot_one = os.path.join(faux_content_dir, "snapshot_01.json")
    snapshot_three = os.path.join(faux_content_dir, "snapshot_03.json")
    snapshot_four = os.path.join(faux_content_dir, "snapshot_04.json")
    paths = [snapshot_one, snapshot_three, snapshot_four]
    # Skipping 2 so we can test how one lost post is handled

    # Assign the empty variables that would normally be handled by init
    master_content_generator.original_post = {}
    master_content_generator.all_replies = {}
    master_content_generator.all_post_ids = set()
    master_content_generator.master_contents = {
        "thread_id": "",
        "original_post": master_content_generator.original_post,
        "replies": master_content_generator.all_replies}
    
    # Assign list of faux paths
    master_content_generator.list_of_content_paths = paths

    # Act & Assert
    master_contents = master_content_generator._generate_master_content()
    
    # Various data points
    assert master_contents["thread_id"] == "00"

    assert master_contents["original_post"]["replied_to_ids"] == (
        ["/b/01"])

    # The method looked at multiple files, kept lost post
    assert master_contents["replies"]["reply_02"] == {
        "date_posted":
            "2025-06-16T10:00:03",
        "post_id": 
            "02",
        "post_content":
            "The five boxing wizards jump quickly.",
        "img_links": 
            ["ex.com/b/t/100.jpg"],
        "username":
            "Brandee Younger",
        "replied_to_ids":
            []}
    assert master_contents["replies"]["reply_03"] == {
        "date_posted":
            "2025-06-16T10:00:03",
        "post_id": 
            "03",
        "post_content":
            "Heavy boxes perform quick waltzes and jigs.",
        "img_links": 
            [],
        "username":
            "Casper Reardon",
        "replied_to_ids":
            ["02"]}