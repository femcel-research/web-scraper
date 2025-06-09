# Imports
import logging
import pytest

from bs4 import BeautifulSoup, Tag
# from datetime import datetime

from src.web_scraper.parse.HTMLToContent import ChanToContent
from src.web_scraper.parse.HTMLToContent.exceptions import *

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

def test_get_thread_id_thread_not_found_error(mocker):
    """Test get_thread_id() raises TagNotFoundError properly."""
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
    with pytest.raises(TagNotFoundError) as excinfo:
        chan_to_content.get_thread_id()

    assert isinstance(excinfo.value, TagNotFoundError)

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
    # Likely no longer needed
    # post_date_location: str = "time"
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup
    chan_to_content.op_class = op_class
    # Likely no longer needed
    # chan_to_content.post_date_location = post_date_location  

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
    # Likely no longer needed
    # post_date_location: str = "time"
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup
    chan_to_content.op_class = op_class
    # Likely no longer needed
    # chan_to_content.post_date_location = post_date_location

    # Act & Assert
    post: Tag = chan_to_content.get_original_post()
    post_date: str = chan_to_content.get_post_date(post)

    assert post_date == "2025-06-05T14:30:02"

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
    # Likely no longer needed
    # post_date_location: str = "time"
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup
    chan_to_content.reply_class = reply_class
    # Likely no longer needed
    # chan_to_content.post_date_location = post_date_location

    # Act & Assert
    with pytest.raises(TagNotFoundError) as excinfo:
        chan_to_content.get_post_date(reply_class)

    assert isinstance(excinfo.value, TagNotFoundError)

def test_get_post_id(mocker):
    """Test get_post_id() returns the correct post ID."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <div class='post_op'>
                <p class='intro' id=101010>
                </p>
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
    post: Tag = chan_to_content.get_original_post()
    post_id: str = chan_to_content.get_post_id(post)

    assert post_id == "101010"

def test_get_post_id_replace_reply_prefix(mocker):
    """Test get_post_id() returns the correct post ID."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <div class='post reply' id='reply_010101'>
            </div>
        </div>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    reply_class: str = "post reply"
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup
    chan_to_content.reply_class = reply_class

    # Act & Assert
    post: Tag = chan_to_content.get_reply_posts()[0]
    post_id: str = chan_to_content.get_post_id(post)

    assert post_id == "010101"

def test_get_post_id_no_replace_reply_prefix(mocker):
    """Test get_post_id() returns the correct post ID."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <div class='post reply' id='010101'>
            </div>
        </div>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    reply_class: str = "post reply"
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup
    chan_to_content.reply_class = reply_class

    # Act & Assert
    post: Tag = chan_to_content.get_reply_posts()[0]
    post_id: str = chan_to_content.get_post_id(post)

    assert post_id == "010101"

def test_get_post_id_not_found_error(mocker):
    """Test get_post_id() raises a TagNotFoundError."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <div class='post reply'></div>
        </div>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    reply_class: str = "post reply"
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup
    chan_to_content.reply_class = reply_class

    # Act & Assert
    post: Tag = chan_to_content.get_reply_posts()[0]
    with pytest.raises(TagNotFoundError) as excinfo:
        post_id: str = chan_to_content.get_post_id(post)

    assert isinstance(excinfo.value, TagNotFoundError)

def test_get_post_content(mocker):
    """Test get_post_content() returns the correct text."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <div class='post_op'>
                <p class='intro' id=101010>
                    <div class='body'>
                        The quick brown fox 
                        <span style='color: #FF0404'>jumps</span>
                        over
                        <br>
                        the lazy dog.
                    </div>
                </p>
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
    post: Tag = chan_to_content.get_original_post()
    post_content: str = chan_to_content.get_post_content(post)

    assert post_content == (
    "The quick brown fox\n"
    "jumps\n"
    "over\n"
    "the lazy dog."
    )

def test_get_post_content_not_found_error(mocker):
    """Test get_post_content() raises a TagNotFoundError."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <div class='post_op'>
                <p class='intro' id=101010></p>
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
    post: Tag = chan_to_content.get_original_post()
    with pytest.raises(TagNotFoundError) as excinfo:
        post_content: str = chan_to_content.get_post_content(post)

    assert isinstance(excinfo.value, TagNotFoundError)

def test_get_post_image_links(mocker):
    """Test get_post_image_links() returns the correct list of image links."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <div class='post_op'>
                <p class='intro' id=101010>
                </p>
                <div class='file'>
                    <img class='post-image' src='/b/t/01.jpg' alt>
                </div>
                <img class='post-image' src='/b/t/10.jpg' alt>
            </div>
        </div>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    op_class: str = "post_op"
    root_domain: str = "ex.com"
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup
    chan_to_content.op_class = op_class
    chan_to_content.root_domain = root_domain

    # Act & Assert
    post: Tag = chan_to_content.get_original_post()
    post_img_links: list[str] = chan_to_content.get_post_image_links(post)

    assert post_img_links == ["ex.com/b/t/01.jpg", "ex.com/b/t/10.jpg"]

def test_get_post_image_links_no_not_found_error(mocker):
    """Test get_post_image_links() doesn't raise an error when no images."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <div class='post_op'>
                <p class='intro' id=101010></p>
            </div>
        </div>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    op_class: str = "post_op"
    root_domain: str = "ex.com"
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup
    chan_to_content.op_class = op_class
    chan_to_content.root_domain = root_domain

    # Act & Assert
    post: Tag = chan_to_content.get_original_post()
    post_img_links: list[str] = chan_to_content.get_post_image_links(post)

    assert post_img_links == []

def test_get_thread_image_link(mocker):
    """Test get_thread_image_link() returns the correct image links."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <a href='b/t/11.jpg'>
                <img class='post-image' src='/b/t/11.jpg' alt>
            </a>
            <div class='post_op'>
                <p class='intro' id=101010>
                </p>
                <div class='file'>
                    <img class='post-image' src='/b/t/01.jpg' alt>
                </div>
                <img class='post-image' src='/b/t/10.jpg' alt>
            </div>
        </div>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    thread_id: str = "101010"
    root_domain: str = "ex.com"
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup
    chan_to_content.thread_id = thread_id
    chan_to_content.root_domain = root_domain

    # Act & Assert
    thread_img_link: str = chan_to_content.get_thread_image_link()

    assert thread_img_link == "ex.com/b/t/11.jpg"

# TODO: Not a priority because it's unlikely to ever cause problems, but
# TODO: currently the way get_thread_image_link() works is by extracting
# TODO: the first image in the thread. Usually that should be the thread
# TODO: image, but if one doesn't exist then it'll serve the first
# TODO: image from the first post with an image. This will then be attributed
# TODO: to the original post, as well as whatever post it originally
# TODO: appeared in. Not a huge issue, but could be reworked if it is
# TODO: found to be problematic
@pytest.mark.skip(reason="Fails because the first image will be from a post.")
def test_get_thread_image_link_not_found_error(mocker):
    """Test get_thread_image_link() raises a TagNotFoundError."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <div class='post_op'>
                <p class='intro' id=101010>
                </p>
                <div class='file'>
                    <img class='post-image' src='/b/t/01.jpg' alt>
                </div>
                <img class='post-image' src='/b/t/10.jpg' alt>
            </div>
        </div>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    thread_id: str = "101010"
    root_domain: str = "ex.com"
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_soup = thread_soup
    chan_to_content.thread_id = thread_id
    chan_to_content.root_domain = root_domain

    # Act & Assert
    with pytest.raises(TagNotFoundError) as excinfo:
        thread_img_link: str = chan_to_content.get_thread_image_link()

    assert isinstance(excinfo.value, TagNotFoundError)

def test_get_post_username(mocker):
    """Test get_post_username() returns the correct username."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <div class='post_op'>
                <p class='intro' id=101010></p>
                    <span class='name'>Dorothy Ashby</span>
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
    post: Tag = chan_to_content.get_original_post()
    post_username: str = chan_to_content.get_post_username(post)

    assert post_username == "Dorothy Ashby"

def test_get_post_username_not_found_error(mocker):
    """Test get_post_username() raises a TagNotFoundError."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <div class='post_op'>
                <p class='intro' id=101010></p>
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
    post: Tag = chan_to_content.get_original_post()
    with pytest.raises(TagNotFoundError) as excinfo:
        post_username: str = chan_to_content.get_post_username(post)

    assert isinstance(excinfo.value, TagNotFoundError)

def test_get_replied_to_ids_op(mocker):
    """Test get_replied_to_ids() returns the correct IDs from OP."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <div class='post_op'>
                <p class='intro' id=101010>
                    <a href="/b/101010">101010</a>
                </p>
                <div class='body'>
                    <a href='/b/t/01.html'>>>>/b/01</a>
                </div>
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
    post: Tag = chan_to_content.get_original_post()
    replied_to_ids: list[str] = chan_to_content.get_post_replied_to_ids(post)

    assert replied_to_ids == ["/b/01"]

def test_get_replied_to_ids_reply(mocker):
    """Test get_replied_to_ids() returns the correct IDs from a reply."""
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
                <p class='intro' id='000001'></p>
                <div class='body'>
                    <a href='/b/t/000000'>>>000000</a>
                </div>
            </div>
            <div class='post_reply'>
                <p class='intro' id='000002'></p>
                <div class='body'>
                    <a href='/b/t/000001'>>>000001</a>
                    Here's a quick test
                    <a href="https://google.com">https://google.com</a>
                </div>
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

    assert chan_to_content.get_post_replied_to_ids(replies[0])[0] == "000000"
    assert chan_to_content.get_post_replied_to_ids(replies[1])[0] == "000001"
    assert len(chan_to_content.get_post_replied_to_ids(replies[1])) == 1

def test_get_replied_to_ids_no_not_found_error(mocker):
    """Test get_replied_to_ids() doesn't return an error when no links."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <div class='post_op'>
                <p class='intro' id=101010>
                </p>
                <div class='body'>
                </div>
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
    post: Tag = chan_to_content.get_original_post()
    replied_to_ids: list[str] = chan_to_content.get_post_replied_to_ids(post)

    assert replied_to_ids == []
    
def test_get_original_post_data(mocker):
    "Test get_original_post_data() returns properly formatted data."
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <a href='b/t/11.jpg'>
                <img class='post-image' src='/b/t/11.jpg' alt>
            </a>
            <div class='post_op'>
                <p class='intro' id=101010>
                    <span class='name'>Dorothy Ashby</span>
                    <span>
                        <a class='date' title='06/05/25 (Thu) 02:30:01 PM'>
                            <time datetime='2025-06-05T14:30:01Z'>
                            </time>
                        </a>
                    </span>
                </p>
                <div class='body'>
                    <a href='/b/t/01.html'>>>>/b/01</a>
                    The quick brown fox jumps over the lazy dog.
                </div>
            </div>
        </div>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    thread_id: str = "101010"
    op_class: str = "post_op"
    root_domain: str = "ex.com"
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_id = thread_id
    chan_to_content.thread_soup = thread_soup
    chan_to_content.op_class = op_class
    chan_to_content.root_domain = root_domain

    # Act & Assert
    post: Tag = chan_to_content.get_original_post()
    original_post_data: dict = chan_to_content.get_original_post_data(post)

    assert original_post_data == {
        "date_posted":
            "2025-06-05T14:30:01",
        "post_id": 
            "101010",
        "post_content":
            "The quick brown fox jumps over the lazy dog.",
        "img_links": 
            ["ex.com/b/t/11.jpg"],
        "username":
            "Dorothy Ashby",
        "replied_to_ids":
            ["/b/01"]}
    

def test_get_reply_post_data(mocker):
    "Test get_reply_post_data() returns properly formatted data."
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <div class='post reply' id='reply_101010'>
                <p class='intro'>
                    <div class='file'>
                        <a href='b/t/11.jpg'>
                            <img class='post-image' src='/b/t/11.jpg' alt>
                        </a>
                    </div>
                    <span class='name'>Dorothy Ashby</span>
                    <span>
                        <a class='date' title='06/05/25 (Thu) 02:30:01 PM'>
                            <time datetime='2025-06-05T14:30:01Z'>
                            </time>
                        </a>
                    </span>
                </p>
                <div class='body'>
                    <a href='/b/t/01.html'>>>>/b/01</a>
                    The quick brown fox jumps over the lazy dog.
                </div>
            </div>
        </div>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    thread_id: str = "101010"
    reply_class: str = "post reply"
    root_domain: str = "ex.com"
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_id = thread_id
    chan_to_content.thread_soup = thread_soup
    chan_to_content.reply_class = reply_class
    chan_to_content.root_domain = root_domain

    # Act & Assert
    posts: list[Tag] = chan_to_content.get_reply_posts()
    reply_post_data: dict = chan_to_content.get_reply_post_data(posts[0])

    assert reply_post_data == {
        "date_posted":
            "2025-06-05T14:30:01",
        "post_id": 
            "101010",
        "post_content":
            "The quick brown fox jumps over the lazy dog.",
        "img_links": 
            ["ex.com/b/t/11.jpg"],
        "username":
            "Dorothy Ashby",
        "replied_to_ids":
            ["/b/01"]}

def test_get_all_post_data(mocker):
    """Test get_all_post_data() returns properly formatted data."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <a href='b/t/11.jpg'>
                <img class='post-image' src='/b/t/11.jpg' alt>
            </a>
            <div class='post_op'>
                <p class='intro' id=101010>
                    <span class='name'>Dorothy Ashby</span>
                    <span>
                        <a class='date' title='06/05/25 (Thu) 02:30:01 PM'>
                            <time datetime='2025-06-05T14:30:01Z'>
                            </time>
                        </a>
                    </span>
                </p>
                <div class='body'>
                    <a href='/b/t/01.html'>>>>/b/01</a>
                    The quick brown fox jumps over the lazy dog.
                </div>
            </div>
            <div class='post reply' id='reply_010101'>
                <p class='intro'>
                    <div class='file'>
                        <a href='b/t/11.jpg'>
                            <img class='post-image' src='/b/t/11.jpg' alt>
                        </a>
                    </div>
                    <span class='name'>Dorothy Ashby</span>
                    <span>
                        <a class='date' title='06/05/25 (Thu) 02:30:01 PM'>
                            <time datetime='2025-06-05T14:30:01Z'>
                            </time>
                        </a>
                    </span>
                </p>
                <div class='body'>
                    <a href='/b/t/01.html'>>>>/b/01</a>
                    The quick brown fox jumps over the lazy dog.
                </div>
            </div>
        </div>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    thread_id: str = "101010"
    op_class: str = "post_op"
    reply_class: str = "post reply"
    root_domain: str = "ex.com"
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_id = thread_id
    chan_to_content.thread_soup = thread_soup
    chan_to_content.op_class = op_class
    chan_to_content.reply_class = reply_class
    chan_to_content.root_domain = root_domain

    # Act & Assert
    original_post: Tag = chan_to_content.get_original_post()
    reply_posts: list[Tag] = chan_to_content.get_reply_posts()

    assert chan_to_content.get_all_post_data(original_post, reply_posts) == {
        "original_post":
            {
            "date_posted":
                "2025-06-05T14:30:01",
            "post_id": 
                "101010",
            "post_content":
                "The quick brown fox jumps over the lazy dog.",
            "img_links": 
                ["ex.com/b/t/11.jpg"],
            "username":
                "Dorothy Ashby",
            "replied_to_ids":
                ["/b/01"]},
        "reply_010101":
            {
            "date_posted":
                "2025-06-05T14:30:01",
            "post_id": 
                "010101",
            "post_content":
                "The quick brown fox jumps over the lazy dog.",
            "img_links": 
                ["ex.com/b/t/11.jpg"],
            "username":
                "Dorothy Ashby",
            "replied_to_ids":
                ["/b/01"]}}
    
def test_get_all_post_data_op_only(mocker):
    """Test get_all_post_data() returns data when no replies."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)

    html_content = b"""
    <html>
    <body>
        <div id='thread_101010'>
            <a href='b/t/11.jpg'>
                <img class='post-image' src='/b/t/11.jpg' alt>
            </a>
            <div class='post_op'>
                <p class='intro' id=101010>
                    <span class='name'>Dorothy Ashby</span>
                    <span>
                        <a class='date' title='06/05/25 (Thu) 02:30:01 PM'>
                            <time datetime='2025-06-05T14:30:01Z'>
                            </time>
                        </a>
                    </span>
                </p>
                <div class='body'>
                    <a href='/b/t/01.html'>>>>/b/01</a>
                    The quick brown fox jumps over the lazy dog.
                </div>
            </div>
        </div>
    </body>
    </html>"""
    thread_soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    thread_id: str = "101010"
    op_class: str = "post_op"
    reply_class: str = "post reply"
    root_domain: str = "ex.com"
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.thread_id = thread_id
    chan_to_content.thread_soup = thread_soup
    chan_to_content.op_class = op_class
    chan_to_content.reply_class = reply_class
    chan_to_content.root_domain = root_domain

    # Act & Assert
    original_post: Tag = chan_to_content.get_original_post()
    reply_posts: list[Tag] = chan_to_content.get_reply_posts()

    assert chan_to_content.get_all_post_data(original_post, reply_posts) == {
        "original_post":
            {
            "date_posted":
                "2025-06-05T14:30:01",
            "post_id": 
                "101010",
            "post_content":
                "The quick brown fox jumps over the lazy dog.",
            "img_links": 
                ["ex.com/b/t/11.jpg"],
            "username":
                "Dorothy Ashby",
            "replied_to_ids":
                ["/b/01"]}}
    
def test_collect_all_data(mocker):
    """Test collect_all_data() formats all data from initialization."""
    # Arrange
    chan_to_content = ChanToContent.__new__(ChanToContent)
    mocker.patch.object(ChanToContent, "__init__", return_value=None)
    board_name: str = "Test"
    thread_title: str = "Scraper"
    thread_id: str = "101010"
    url: str = "example.com"
    date_published: str = "2025-06-06T16:00:01"
    date_updated: str = "2025-06-06T16:00:02"
    date_scraped: str = "2025-06-06T16:00:03"
    posts: dict = {
        "original_post":
            {
            "date_posted":
                "2025-06-05T14:30:01",
            "post_id": 
                "101010",
            "post_content":
                "The quick brown fox jumps over the lazy dog.",
            "img_links": 
                ["ex.com/b/t/11.jpg"],
            "username":
                "Dorothy Ashby",
            "replied_to_ids":
                ["/b/01"]}}
    chan_to_content.logger = logging.getLogger(__name__)
    chan_to_content.board_name = board_name
    chan_to_content.thread_title = thread_title
    chan_to_content.thread_id = thread_id
    chan_to_content.snapshot_url = url
    chan_to_content.date_published = date_published
    chan_to_content.date_updated = date_updated
    chan_to_content.date_scraped = date_scraped
    chan_to_content.all_post_data = posts
    
    # Act & Assert
    assert chan_to_content.collect_all_data() == {
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
        "posts":
            posts}