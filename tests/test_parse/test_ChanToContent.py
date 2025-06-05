# Imports
import logging
import pytest

from bs4 import BeautifulSoup, Tag
# from datetime import datetime

from web_scraper.parse.HTMLtoContent.ChanToContent import ChanToContent
from web_scraper.parse.HTMLtoContent.exceptions import *

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

def test_get_board_name_and_thread_title(mocker):
    """Test get_board_name_and_thread_title() captures data from a soup ob."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <head>
        <title>/scraping/ - ChanToContent Dev Thread</title> == $0
    </head>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup

    # Act & Assert
    assert chan_to_content.get_board_name_and_thread_title()\
        ["board"] == "/scraping/"
    assert chan_to_content.get_board_name_and_thread_title()\
        ["title"] == "ChanToContent Dev Thread"

def test_get_board_name_and_thread_title_not_found_error(mocker):
    """Test get_board_name_and_thread_title() raises BoardNameAndTitleNotFoundError."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <head>
    </head>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup

    # Act & Assert
    with pytest.raises(BoardNameAndTitleNotFoundError) as excinfo:
        chan_to_content.get_board_name_and_thread_title()

    assert isinstance(excinfo.value, BoardNameAndTitleNotFoundError)

def test_get_board_name_and_thread_title_unsupported_error(mocker):
    """Test get_board_name_and_thread_title() raises BoardNameAndTitleUnsupportedError."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <head>
        <title>/scraping/ | ChanToContent Dev Thread</title>
    </head>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup

    # Act & Assert
    with pytest.raises(BoardNameAndTitleUnsupportedError) as excinfo:
        chan_to_content.get_board_name_and_thread_title()

    assert isinstance(excinfo.value, BoardNameAndTitleUnsupportedError)

# TODO: There's room to add some better tests for the htmldate that is used
# TODO: in get_date_published_and_updated(), but I would need to spend more
# TODO: time figuring out how to best test it

def test_get_date_published_and_updated_not_found_error(mocker):
    """Test get_date_published_and_updated() raises DateNotFoundError."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <head>
    </head>
    <body>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup

    # Act & Assert
    with pytest.raises(DateNotFoundError) as excinfo:
        chan_to_content.get_date_published_and_updated()

    assert isinstance(excinfo.value, DateNotFoundError)

def test_get_original_post(mocker):
    """Test get_original_post() returns the correct Tag."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <div class='post_op'>
                <p class='intro' id='101010'>
                </p>
            </div>
            <div class='post_reply'>
            </div>
        </div>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    op_class: str = "post_op"
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup
    chan_to_content.op_class = op_class

    # Act & Assert
    # Retrieving with ["class"] returns a list
    assert chan_to_content.get_original_post()["class"][0] == op_class
    assert isinstance(chan_to_content.get_original_post(), Tag)

def test_get_original_post_not_found_error(mocker):
    """Test get_original_post() raises TagNotFoundError."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <div class='post_reply'>
            </div>
        </div>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    op_class: str = "post_op"
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup
    chan_to_content.op_class = op_class

    # Act & Assert
    with pytest.raises(TagNotFoundError) as excinfo:
        chan_to_content.get_original_post()

    assert isinstance(excinfo.value, TagNotFoundError)

def test_get_reply_posts(mocker):
    """Test get_reply_posts() returns the correct list of Tags."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <div class='post_op'>
            </div>
            <div class='post_reply'>
                <p class='intro' id='000001'>
                </p>
            </div>
            <div class='post_reply'>
                <p class='intro' id='000002'>
                </p>
            </div>
        </div>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    reply_class: str = "post_reply"
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup
    chan_to_content.reply_class = reply_class

    # Act & Assert the post replies were collected linearly, and only replies
    # were collected
    replies: list[Tag] = chan_to_content.get_reply_posts()
    assert replies[0].find(class_="intro").get("id") == "000001"
    assert replies[1].find(class_="intro").get("id") == "000002"

    assert len(replies) == 2

    assert isinstance(chan_to_content.get_reply_posts(), list)

def test_get_reply_posts_no_not_found_error(mocker):
    """Test get_reply_posts() doesn't raise an error if no replies."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <div class='post_op'>
            </div>
        </div>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    reply_class: str = "post_reply"
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup
    chan_to_content.reply_class = reply_class

    # Act & Assert
    replies: list[Tag] = chan_to_content.get_reply_posts()
    assert len(replies) == 0

    assert isinstance(chan_to_content.get_reply_posts(), list)

def test_get_post_date(mocker):
    """Test get_post_date() returns the correct post date."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <div class='post_op'>
                <p class='intro' id= 101010'>
                    <span>
                        <a class='date' title='06/05/25 (Thu) 02:30:01 PM'>
                            <time datetime='2025-06-05T14:30:01Z'>
                            </time>
                        </a>
                    </span>
                </p>
            </div>
        </div>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    op_class: str = "post_op"
    post_date_location: str = "time"
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup
    chan_to_content.op_class = op_class
    chan_to_content.post_date_location = post_date_location

    # Act & Assert 
    post: Tag = chan_to_content.get_original_post()
    post_date: str = chan_to_content.get_post_date(post)

    assert post_date == "2025-06-05T14:30:01"

def test_get_post_date_alternative(mocker):
    """Test get_post_date() returns the correct post date."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <div class='post_op' id='101010'>
                <p class='intro'>
                    <label for='post_op'>
                        <time datetime='2025-06-05T14:30:02Z'>
                        </time>
                    </label>
                </p>
            </div>
        </div>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    op_class: str = "post_op"
    post_date_location: str = "time"
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup
    chan_to_content.op_class = op_class
    chan_to_content.post_date_location = post_date_location

    # Act & Assert
    post: Tag = chan_to_content.get_original_post()
    post_date: str = chan_to_content.get_post_date(post)

def test_get_post_date_not_found_error(mocker):
    """Test get_post_date() raises a TagNotFoundError."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <div class='post_reply'>
            </div>
        </div>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    reply_class: str = "post_op"
    post_date_location: str = "time"
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup
    chan_to_content.reply_class = reply_class
    chan_to_content.post_date_location = post_date_location

    # Act & Assert
    with pytest.raises(TagNotFoundError) as excinfo:
        chan_to_content.get_post_date(reply_class)

    assert isinstance(excinfo.value, TagNotFoundError)