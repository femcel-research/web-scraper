import glob
import os
import pytest


from web_scraper.parse.MasterContentGenerator import MasterContentGenerator


def test_meta_content_generation():
    # Finds list of snapshot paths from dummy data
    dummy_data_dir = "./tests/dummy_data"
    candidate_content_files = os.path.join(dummy_data_dir, "**", "content_*.json")
    list_of_snapshot_paths: list[str] = list(
        glob.glob(candidate_content_files, recursive=True)
    )

    # Generates master content
    master_content_generator = MasterContentGenerator(list_of_snapshot_paths)
    master_content = master_content_generator.generate_master_content()

    # Original post & replies in the generated master
    master_original_post = master_content["original_post"]
    master_replies = master_content["replies"]

    # Original post from the dummy data folder
    snapshot_original_post = {
        "post_id": "431",
        "username": "Anonymous",
        "reply_to_another_thread?": False,
        "date_posted": "2017-05-27T23:31:22",
        "image_links": [],
        "post_content": "Post your skincare questions, routines, recommendations, rants, raves, product recs, etc. I'll start with my routine that's finally working for me: AM: Thayer's unscented witch hazel (as a toner) COSRX Oil-Free Ultra Moisturizing Lotion CeraVe AM Facial Moisturizing Lotion PM: Pond's cold cream cleanser Thayer's witch hazel toner Cosrx BHA Blackhead Power Liquid (leave on for 15 minutes) Oil cleanse with mineral oil Remove with Pond's cold cream cleanser COSRX Oil-Free Ultra Moisturizing Lotion CeraVe Moisturizing Cream A big ol' slab of vaseline all over my face",
        "replied_thread_ids": [],
    }

    # Assertions:
    assert isinstance(master_content, dict)
    assert master_content["thread_id"] == "431"

    assert isinstance(master_original_post, dict)
    assert master_original_post == snapshot_original_post

    assert isinstance(master_replies, dict)
    assert isinstance(
        master_replies["reply_432"], dict
    )  # Roundabout way of testing to see if this reply is present by looking for a specific ID.
