import pytest
from web_scraper.parse.JSONToContent import SourceToContent


@pytest.fixture
def sample_json_with_sub():
    """Sample JSON for a thread with 'sub' (subtitle)."""
    return {
        "posts": [
            {
                "no": 12345,
                "time": 1678886400,
                "sub": "10 Game Winstreak",
                "com": "This is the <b>original</b> post comment with <br>multiple lines.",
                "name": "Anonymous",
                "resto": 0,
                "tim": 1678886400000,
                "ext": ".jpg",
                "trip": "!tripcode123"
            },
            {
                "no": 12346,
                "time": 1678886500,
                "com": "First reply <br>Testing. <a href='test'>link</a>",
                "name": "Replier",
                "resto": 12345,
                "tim": 1678886500000,
                "ext": ".png",
            },
            {
                "no": 12347,
                "time": 1678886600,
                "com": "Second reply with only text.",
                "name": "Anonymous",
                "resto": 12345,
                "trip": "!!anontrip"
            },
            {
                "no": 12348,
                "time": 1678886700,
                "com": "Third reply, no image, no tripcode.",
                "name": "Anonymous",
                "resto": 12346,
            }
        ]
    }


@pytest.fixture
def sample_json_with_semantic_url():
    """Sample JSON for a thread without 'sub' but with 'semantic_url'."""
    return {
        "posts": [
            {
                "no": 54321,
                "time": 1679059200,
                "semantic_url": "test-thread-example",
                "com": "I like playing Overwatch. It is fun.",
                "name": "Anonymous",
                "resto": 0,
            }
        ]
    }


@pytest.fixture
def sample_json_no_comment_no_image():
    """Sample JSON for a post with no comment and no image."""
    return {
        "posts": [
            {
                "no": 98765,
                "time": 1679145600,  # 2023-03-18 00:00:00 UTC
                "sub": "Empty Post Thread",
                "name": "Anonymous",
                "resto": 0,
            }
        ]
    }


class TestSourceToContent:

    def test_init_with_subtitle(self, sample_json_with_sub):
        board_name = "b"
        scan_time = "2023-03-15 10:00:00"
        source_to_content = SourceToContent(
            board_name, sample_json_with_sub, scan_time)

        assert source_to_content.board_name == board_name
        assert source_to_content.thread_title == "10 Game Winstreak"
        assert source_to_content.thread_id == "12345"
        assert source_to_content.thread_url == f"https://boards.4chan.org/{board_name}/thread/12345"
        assert source_to_content.scrape_time == scan_time
        assert source_to_content.data["board_name"] == board_name
        assert source_to_content.data["thread_title"] == "10 Game Winstreak"
        assert source_to_content.data["thread_id"] == "12345"
        assert source_to_content.data[
            "url"] == f"https://boards.4chan.org/{board_name}/thread/12345"
        assert source_to_content.data["date_published"] == "2023-03-15T08:20:00"
        # Latest post date
        assert source_to_content.data["date_updated"] == "2023-03-15T08:25:00"
        assert source_to_content.data["date_scraped"] == scan_time

        # Ensure op structure is the same
        op_data = source_to_content.data["original_post"]
        assert op_data["post_id"] == "12345"
        assert op_data["post_content"] == "This is the original post comment with\nmultiple lines."
        assert op_data["img_links"] == [
            "http://i.4cdn.org/b/1678886400000.jpg"]
        assert op_data["username"] == "Anonymous"
        assert op_data["tripcode"] == "!tripcode123"
        assert op_data["replied_to_ids"] == []

        # Ensure reply structure is the same
        replies = source_to_content.data["replies"]
        assert len(replies) == 3
        assert "reply_12346" in replies
        assert "reply_12347" in replies
        assert "reply_12348" in replies

        # No tripcode
        reply1_data = replies["reply_12346"]
        assert reply1_data["post_id"] == "12346"
        assert reply1_data["post_content"] == "First reply\nTesting. link"
        assert reply1_data["img_links"] == [
            "http://i.4cdn.org/b/1678886500000.png"]
        assert reply1_data["username"] == "Replier"
        assert reply1_data["tripcode"] == ""
        assert reply1_data["replied_to_ids"] == [12345]

        # No img
        reply2_data = replies["reply_12347"]
        assert reply2_data["post_id"] == "12347"
        assert reply2_data["post_content"] == "Second reply with only text."
        assert reply2_data["img_links"] == []
        assert reply2_data["username"] == "Anonymous"
        assert reply2_data["tripcode"] == "!!anontrip"
        assert reply2_data["replied_to_ids"] == [12345]

        # No img or tripcode
        reply3_data = replies["reply_12348"]
        assert reply3_data["post_id"] == "12348"
        assert reply3_data["post_content"] == "Third reply, no image, no tripcode."
        assert reply3_data["img_links"] == []
        assert reply3_data["username"] == "Anonymous"
        assert reply3_data["tripcode"] == ""
        assert reply3_data["replied_to_ids"] == [12346]

    def test_init_with_semantic_url(self, sample_json_with_semantic_url):
        board_name = "g"
        scan_time = "2023-03-17T12:00:00"
        source_to_content = SourceToContent(
            board_name, sample_json_with_semantic_url, scan_time)

        assert source_to_content.thread_title == "test thread example"
        assert source_to_content.thread_id == "54321"
        assert source_to_content.thread_url == f"https://boards.4chan.org/{board_name}/thread/54321"
        assert source_to_content.data["thread_title"] == "test thread example"

    def test_generate_post_data(self, sample_json_with_sub):
        source_to_content = SourceToContent(
            "a", sample_json_with_sub, "2000")

        post_data = {
            "no": 123,
            "time": 1678972800,
            "com": "Test <b>comment</b> with <br>html.",
            "name": "Anonymous",
            "resto": 456,
            "tim": 1678972800000,
            "ext": ".gif",
            "trip": "!!testtrip",
            "semantic_url": "fortnite"
        }
        result = source_to_content.generate_post_data(post_data)

        assert result["date_posted"] == "2023-03-16T08:20:00"
        assert result["post_id"] == "123"
        assert result["post_content"] == "Test comment with\nhtml."
        assert result["img_links"] == ["http://i.4cdn.org/a/1678972800000.gif"]
        assert result["username"] == "Anonymous"
        assert result["tripcode"] == "!!testtrip"
        assert result["replied_to_ids"] == [456]

    def test_generate_post_data_no_comment_no_image(self, sample_json_with_sub):
        source_to_content = SourceToContent(
            "a", sample_json_with_sub, "2000")

        post_data = {
            "no": 789,
            "time": 1679059200,
            "name": "Anonymous",
            "resto": 0,
        }
        result = source_to_content.generate_post_data(post_data)

        assert result["post_id"] == "789"
        assert result["post_content"] == ""
        assert result["img_links"] == []
        assert result["username"] == "Anonymous"
        assert result["tripcode"] == ""
        assert result["replied_to_ids"] == []

    def test_generate_post_data_op_post(self, sample_json_with_sub):
        source_to_content = SourceToContent(
            "a", sample_json_with_sub, "2000")

        post_data = {
            "no": 101,
            "time": 1679145600,
            "com": "Original post content.",
            "name": "OP",
            "resto": 0,  # resto is 0 for OP bc OP shouldnt be replying to posts in same thread
        }
        result = source_to_content.generate_post_data(post_data)
        assert result["replied_to_ids"] == []

    def test_fetch_latest_date(self, sample_json_with_sub):
        board_name = "b"
        scan_time = "2023-03-15 10:00:00"
        source_to_content = SourceToContent(
            board_name, sample_json_with_sub, scan_time)
        latest_date = source_to_content.fetch_latest_date(
            source_to_content.posts)
        assert latest_date == "2023-03-15T08:25:00"

    def test_clean_comment_text(self, sample_json_with_sub):
        source_to_content = SourceToContent(
            "a", sample_json_with_sub, "2000")

        # Test with various HTML tags and line breaks
        comment = "<br>New line.<br/> Another line."
        expected = "\nNew line. Another line."
        assert source_to_content.clean_comment_text(comment) == expected

        comment = "No HTML."
        expected = "No HTML."
        assert source_to_content.clean_comment_text(comment) == expected

        comment = "<p>Paragraph</p> with <span>span</span> and <br> space."
        expected = "Paragraph with span and\nspace."
        assert source_to_content.clean_comment_text(comment) == expected

        comment = "Text with \n extra space after newline. "
        expected = "Text with\nextra space after newline. "
        assert source_to_content.clean_comment_text(comment) == expected

        comment = "Text with \n extra space before newline."
        expected = "Text with\nextra space before newline."
        assert source_to_content.clean_comment_text(comment) == expected
