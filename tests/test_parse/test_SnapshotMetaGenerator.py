# Imports
import json
import os
import pytest

from web_scraper.parse.SnapshotMetaGenerator import SnapshotMetaGenerator

@pytest.fixture
def faux_content_dir(fs):
    """Custom fixture to create a fake data directory with snapshot files."""
    faux_thread_dir = "/faux_thread"
    snapshot_one = os.path.join(faux_thread_dir, "snapshot_1.json")
    snapshot_two = os.path.join(faux_thread_dir, "snapshot_2.json")
    snapshot_three = os.path.join(faux_thread_dir, "snapshot_3.json")

    # Create fake snapshot content data
    # (Likely don't need all of this for testing, but I would rather be
    # safe and be able to repurpose this fixture for other tests)
    board_name: str = "Test"
    thread_title: str = "Scraper"
    thread_id: str = "0"
    url: str = "example.com"
    date_published: str = "2025-06-16T10:00:01"
    date_updated: str = "2025-06-16T10:00:03"
    date_scraped: str = "2025-06-16T10:00:04"
    original_post: dict = {
        "date_posted":
            "2025-06-16T10:00:01",
        "post_id": 
            "0",
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
            "1",
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
            "2",
        "post_content":
            "The five boxing wizards jump quickly.",
        "img_links": 
            ["ex.com/b/t/100.jpg"],
        "username":
            "Brandee Younger",
        "replied_to_ids":
            []}

    empty_replies: dict = {}
    one_reply: dict = {"reply_1": first_reply}
    two_replies: dict = {"reply_1": first_reply, "reply_2": second_reply}
    
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

    assert content["thread_id"] == "0"

def test__generate_meta(mocker, faux_content_dir):
    """Test the _generate_meta() method returns a correct dict."""
    # Arrange
    snapshot_meta_generator = SnapshotMetaGenerator.__new__(
        SnapshotMetaGenerator)
    mocker.patch.object(SnapshotMetaGenerator, "__init__", return_value=None)

    snapshot_3 = os.path.join(faux_content_dir, "snapshot_3.json")

    # Assign the variables that would normally be handled by init
    with open(snapshot_3, "r", encoding="utf-8") as file:
        content = json.load(file)
    
    snapshot_meta_generator.content_json = content
    snapshot_meta_generator.thread_id = content["thread_id"]
    snapshot_meta_generator.original_post = content["original_post"]
    snapshot_meta_generator.replies = content["replies"]

    # Act & Assert
    snapshot_meta = snapshot_meta_generator._generate_meta()

    assert isinstance(snapshot_meta, dict)
    assert snapshot_meta["board_name"] == content["board_name"]
    assert snapshot_meta["thread_title"] == content["thread_title"]
    assert snapshot_meta["thread_id"] == content["thread_id"]
    assert snapshot_meta["url"] == content["url"]
    assert snapshot_meta["date_published"] == content["date_published"]
    assert snapshot_meta["date_updated"] == content["date_updated"]
    assert snapshot_meta["num_all_post_ids"] == 3   


# TODO: Also write test for init using file path
