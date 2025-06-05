import pytest


from web_scraper.parse.MasterContentGenerator import MasterContentGenerator


def test_MetaContentGenerator_generation():
    dummy_data_dir = "./tests/dummy_data"
    list_of_snapshot_paths: list[str] = dummy_data_dir.glob("content_*.json")
    master_content_generator = MasterContentGenerator(list_of_snapshot_paths)
    master_content = master_content_generator.get_master_content()
    
    assert isinstance(master_content, dict)
    assert master_content["thread_id"] == "431"
    assert master_content["original_post"] == {
      "post_id": "431",
      "username": "Anonymous",
      "reply_to_another_thread?": "false",
      "date_posted": "2017-05-27T23:31:22",
      "image_links": [],
      "post_content": "Post your skincare questions, routines, recommendations, rants, raves, product recs, etc. I'll start with my routine that's finally working for me: AM: Thayer's unscented witch hazel (as a toner) COSRX Oil-Free Ultra Moisturizing Lotion CeraVe AM Facial Moisturizing Lotion PM: Pond's cold cream cleanser Thayer's witch hazel toner Cosrx BHA Blackhead Power Liquid (leave on for 15 minutes) Oil cleanse with mineral oil Remove with Pond's cold cream cleanser COSRX Oil-Free Ultra Moisturizing Lotion CeraVe Moisturizing Cream A big ol' slab of vaseline all over my face",
      "replied_thread_ids": []
   }
    
    print(master_content)