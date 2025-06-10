# Imports
import os
import pytest

from web_scraper.parse import MasterTextGenerator

@pytest.fixture
def mock_master_content(mocker):
    """Fixture to create a mock master content dictionary."""
    master_content: dict = {
        "thread_id": "101010",
        "original_post": {
            "post_id": "01",
            "username": "Anonymous",
            "date_posted": "2025-06-09T14:56:00",
            "image_links": ["example.com/image"],
            "post_content": "The quick brown fox jumps over a lazy \ndog!",
            "replied_thread_ids": []
        },
        "replies": {
            "reply_10": {
                "post_id": "10",
                "username": "Anonymous",
                "date_posted": "2025-06-09T14:56:01",
                "image_links": ["example.com/image2"],
                "post_content": "Sphinx of black quartz judge my vow...",
                "replied_to_ids": ["01"]
            },
            "reply_11": {
                "post_id": "11",
                "username": "Anonymous",
                "date_posted": "2025-06-09T14:56:01",
                "image_links": ["example.com/image2"],
                "post_content": "Is it panagram day?",
                "replied_to_ids": ["01", "10"]
            }
        }
    }
    return master_content

# def test_write_text(mocker, mock_master_content):
#     """Tests write_text() works properly with a populated JSON."""
#     # Arrange
#     master_text_generator: MasterTextGenerator = (
#         MasterTextGenerator.__new__(MasterTextGenerator))
#     mocker.patch.object(MasterTextGenerator, "__init__", return_value=None)

#     master_text_generator.content = mock_master_content
#     master_text_generator.master_text_path = os.path.join("..", "dummy_data")
#     # Write to a mocked master content file
#     # mocked_open_text = mocker.mock_open()
#     # mocker.patch("MasterTextGenerator.open")
#     master_text_generator.write_text()
    

# def test_empty_write_out(mocker, mock_master_content):
#     """Tests an RTF file is created."""
#     # Arrange
#     master_text_generator = MasterTextGenerator.__new__(MasterTextGenerator)
#     mocker.patch.object(MasterTextGenerator, "__init__", return_value=None)

#     master_text_generator.file = (
#             f"master_text_{mock_master_content["thread_id"]}.rtf", 'w')
#     test_document = Elements.Document()
#     test_section = Elements.Section()
#     test_section.append("Test")
#     master_text_generator.master_text_document = test_document

#     # Act & Assert
#     master_text_generator._write_out()