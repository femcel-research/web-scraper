# Imports
import logging
import pytest

from bs4 import BeautifulSoup
from datetime import datetime

from web_scraper.parse.HTMLToContent.ChanToContent import (
    ChanToContent
)
from web_scraper.parse.HTMLToContent.exceptions import (
    ContentInitError,
    ThreadIDNotFoundError
)

def test_get_thread_id_no_replace_prefix(mocker):
    """Test get_thread_id() captures a thread ID from a soup's HTML."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <p class='intro' id='101010'>
            </p>
        </div>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup

    # Act & Assert the thread IDs in ChanToContent is correct
    assert chan_to_content.get_thread_id() == "101010"

def test_get_thread_id_yes_replace_prefix(mocker):
    """Test get_thread_id() captures a thread ID from a soup's HTML."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div class='post op' id='op_101010'>
            <p class='intro'>
                <a class='post_no' id='post_no_101010'>
                </a>
            </p>
        </div>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup

    # Act & Assert the thread IDs in ChanToContent is correct
    assert chan_to_content.get_thread_id() == "101010"

def test_get_thread_id_thread_id_not_found_error(mocker):
    """Test get_thread_id() raises ThreadIDNotFoundError properly."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <head>
        <title>/scraping/ - ChanToContent Dev Thread</title> == $0
    </head>
    <body>
        <div class='post op'>
            <p class='intro'>
                <a class='post_no'>
                </a>
            </p>
        </div>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup

    # Act & Assert
    with pytest.raises(ThreadIDNotFoundError) as excinfo:
        chan_to_content.get_thread_id()
        
    assert isinstance(excinfo.value, ThreadIDNotFoundError)

# def test_get_board_name_and_thread_title():
#     """Test get_board_name_and_thread_title() captures data from a soup ob."""
#     # Arrange
#     html_content = b"""
#     <html>
#     <head>
#         <title>/scraping/ - ChanToContent Dev Thread</title> == $0
#     </head>
#     <body>
#         <div id='thread_101010'>
#             <p class='intro' id='101010'>
#             </p>
#         </div>
#     </body>
#     </html>"""
#     thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")

#     # Act
#     chan_to_content = ChanToContent(
#         datetime.now(), thread_soup, "", "", "", "", "", "")

#     # Assert the thread IDs in ChanToContent is correct
#     assert chan_to_content.board_name == "/scraping/"
#     assert chan_to_content.thread_title == "ChanToContent Dev Thread"

# def test_get_board_name_and_thread_title_not_found_error():
#     """Test get_board_name_and_thread_title() raises ContentInitError.
    
#     A ContentInitError from a BoardNameAndTitleNotFoundError should be
#     raised.
#     """
#     # Arrange
#     html_content = b"""
#     <html>
#     <head>
#     </head>
#     <body>
#         <div class='post op'>
#             <p class='intro'>
#                 <a class='post_no'>
#                 </a>
#             </p>
#         </div>
#     </body>
#     </html>"""
#     thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")

#     # Act & Assert
#     with pytest.raises(ContentInitError) as excinfo:
#         chan_to_content = ChanToContent(
#         datetime.now(), thread_soup, "", "", "", "", "", "")

#     # Assert
#     assert isinstance(excinfo.value, ContentInitError)
#     # Check the original exception is chained
#     assert "Page title unable to be located" in str(excinfo.value.__cause__)

# def test_get_board_name_and_thread_title_unsupported_error():
#     """Test get_board_name_and_thread_title() raises ContentInitError.
    
#     A ContentInitError from a BoardNameAndTitleUnsupportedError should be
#     raised.
#     """
#     # Arrange
#     html_content = b"""
#     <html>
#     <head>
#         <title>/scraping/ | ChanToContent Dev Thread</title>
#     </head>
#     <body>
#         <div class='post op'>
#             <p class='intro'>
#                 <a class='post_no'>
#                 </a>
#             </p>
#         </div>
#     </body>
#     </html>"""
#     thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")

#     # Act & Assert
#     with pytest.raises(ContentInitError) as excinfo:
#         chan_to_content = ChanToContent(
#         datetime.now(), thread_soup, "", "", "", "", "", "")

#     # Assert
#     assert isinstance(excinfo.value, ContentInitError)
#     # Check the original exception is chained
#     assert "Board name/title unable to be parsed." in str(
#         excinfo.value.__cause__)

# def test_get_date_published_and_updated_not_found_error():
#     """Test get_date_published_and_updated() raises ContentInitError.
    
#     A ContentInitError from a DateNotFoundError should be raised.
#     """
#     # Arrange
#     html_content = b"""
#     <html>
#     <head>
#         <title>/scraping/ | ChanToContent Dev Thread</title>
#     </head>
#     <body>
#         <div class='post op'>
#             <p class='intro'>
#                 <a class='post_no'>
#                 </a>
#             </p>
#         </div>
#     </body>
#     </html>"""
#     thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")

#     # Act & Assert
#     with pytest.raises(ContentInitError) as excinfo:
#         chan_to_content = ChanToContent(
#         datetime.now(), thread_soup, "", "", "", "", "", "")

#     # Assert
#     assert isinstance(excinfo.value, ContentInitError)
#     # Check the original exception is chained
#     assert "Date published not found." in str(
#         excinfo.value.__cause__)