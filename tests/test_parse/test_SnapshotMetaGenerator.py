import glob
import json
import os
import pytest


from web_scraper.parse.SnapshotMetaGenerator import SnapshotMetaGenerator

def test_snapshot_generation():
    # Content path from dummy data
    dummy_content_filepath = "./tests/dummy_data/431/2025-06-02T20:29:04/content_431.json"
    
    # Generates snapshot content
    meta_generator = SnapshotMetaGenerator(dummy_content_filepath)
    snapshot_meta = meta_generator.generate_meta()

    #Compare with dummy meta
    dummy_meta_filepath = "tests/dummy_data/431/2025-06-02T20:29:04/meta_431.json"
    with open(dummy_meta_filepath, "r") as file:
            data = json.load(file)
    dummy_meta = data

    # General board/thread info
    board_name: str = snapshot_meta["board_name"]
    thread_title: str = snapshot_meta["thread_title"]
    thread_id: str = snapshot_meta["thread_id"]
    url: str = snapshot_meta["url"]

    # Data relating to dates/time:
    date_published: str = snapshot_meta["date_published"]
    date_updated: str = snapshot_meta["date_updated"]

    # Data relating to post ids
    all_post_ids: set = set(snapshot_meta["all_post_ids"])
    num_all_post_ids: int = snapshot_meta["num_all_post_ids"]

     # Assertions:
    assert isinstance(snapshot_meta, dict)
    assert board_name == dummy_meta["board_name"]
    assert thread_title == dummy_meta["thread_title"]
    assert thread_id == dummy_meta["thread_id"]
    assert url == dummy_meta["url"]
    assert date_published == dummy_meta["date_published"]
    assert date_updated == dummy_meta["date_updated"]
    assert num_all_post_ids == dummy_meta["num_all_post_ids"]
    for id in all_post_ids:
        assert id in dummy_meta["all_post_ids"]

   