# Imports
import pytest

from bs4 import BeautifulSoup
from datetime import datetime

from web_scraper.parse.HTMLToContent.ChanToContent import (
    ChanToContent
)
from web_scraper.parse.HTMLToContent.exceptions import (
    ContentInitError
)

def test_get_thread_id_no_replace_prefix():
    """Test get_thread_id() captures a thread ID from a soup's HTML."""
    # Arrange
    html_content = b"""
    <html>
    <head>
        <title>/scraping/ - ChanToContent Dev Thread</title> == $0
    </head>
    <body>
        <div id='thread_101010'>
            <p class='intro' id='101010'>
            </p>
        </div>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")

    # Act
    chan_to_content = ChanToContent(
        datetime.now(), thread_soup, "", "", "", "", "", "")

    # Assert the thread IDs in ChanToContent is correct
    assert chan_to_content.thread_id == "101010"

def test_get_thread_id_yes_replace_prefix():
    """Test get_thread_id() captures a thread ID from a soup's HTML."""
    # Arrange
    html_content = b"""
    <html>
    <head>
        <title>/scraping/ - ChanToContent Dev Thread</title> == $0
    </head>
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

    # Act
    chan_to_content = ChanToContent(
        datetime.now(), thread_soup, "", "", "", "", "", "")

    # Assert the thread IDs in ChanToContent is correct
    assert chan_to_content.thread_id == "101010"

def test_get_thread_id_thread_id_not_found_error():
    """Test get_thread_id() raises ContentInitError from ThreadIDNotFound."""
    # Arrange
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

    # Act & Assert
    with pytest.raises(ContentInitError) as excinfo:
        chan_to_content = ChanToContent(
        datetime.now(), thread_soup, "", "", "", "", "", "")

    # Assert
    assert isinstance(excinfo.value, ContentInitError)
    # Check the original exception is chained
    assert "Thread ID unable to be located" in str(excinfo.value.__cause__) 

def test_get_board_name_and_thread_title():
    """Test get_board_name_and_thread_title() captures data from a soup ob."""
    # Arrange
    html_content = b"""
    <html>
    <head>
        <title>/scraping/ - ChanToContent Dev Thread</title> == $0
    </head>
    <body>
        <div id='thread_101010'>
            <p class='intro' id='101010'>
            </p>
        </div>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")

    # Act
    chan_to_content = ChanToContent(
        datetime.now(), thread_soup, "", "", "", "", "", "")

    # Assert the thread IDs in ChanToContent is correct
    assert chan_to_content.board_name == "/scraping/"
    assert chan_to_content.thread_title == "ChanToContent Dev Thread"

def test_get_board_name_and_thread_title_not_found_error():
    """Test get_board_name_and_thread_title() raises ContentInitError.
    
    A ContentInitError from a BoardNameAndTitleNotFoundError should be
    raised.
    """
    # Arrange
    html_content = b"""
    <html>
    <head>
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

    # Act & Assert
    with pytest.raises(ContentInitError) as excinfo:
        chan_to_content = ChanToContent(
        datetime.now(), thread_soup, "", "", "", "", "", "")

    # Assert
    assert isinstance(excinfo.value, ContentInitError)
    # Check the original exception is chained
    assert "Page title unable to be located" in str(excinfo.value.__cause__)

def test_get_board_name_and_thread_title_unsupported_error():
    """Test get_board_name_and_thread_title() raises ContentInitError.
    
    A ContentInitError from a BoardNameAndTitleUnsupportedError should be
    raised.
    """
    # Arrange
    html_content = b"""
    <html>
    <head>
        <title>/scraping/ | ChanToContent Dev Thread</title>
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

    # Act & Assert
    with pytest.raises(ContentInitError) as excinfo:
        chan_to_content = ChanToContent(
        datetime.now(), thread_soup, "", "", "", "", "", "")

    # Assert
    assert isinstance(excinfo.value, ContentInitError)
    # Check the original exception is chained
    assert "Board name/title unable to be parsed." in str(
        excinfo.value.__cause__)
