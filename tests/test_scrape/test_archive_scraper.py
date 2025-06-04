# Imports
import pytest

from bs4 import BeautifulSoup

from web_scraper.scrape.archive_scraper import (
    ArchiveScraper,
    SoupError,
    TagNotFoundError,
    NoThreadLinkFoundError,
)

def test_archive_scraper_init_success():
    """Test successful initialization of ArchiveScraper with valid HTML."""
    # Arrange
    html_content = b"<html><body><div class='post'></div></body></html>"
    html_tag = "div"
    post_control = "View"

    # Act
    scraper = ArchiveScraper(html_content, html_tag, post_control)

    # Assert
    assert isinstance(scraper.soup, BeautifulSoup)
    assert scraper.html_tag == html_tag
    assert scraper.post_control == post_control

def test_archive_scraper_init_soup_error(mocker):
    """Test __init__ raises SoupError for invalid HTML content."""
    # Arrange
    # Mock BeautifulSoup to raise an exception during initialization
    mock_beautifulsoup = mocker.patch(
        "web_scraper.scrape.archive_scraper.BeautifulSoup")
    mock_beautifulsoup.side_effect = Exception(
        "Mock BeautifulSoup Initialization Error")

    html_content = b"<html><body<div class='post'></body></html>"  # Invalid HTML
    html_tag = "div"
    post_control = "Reply"

    # Act & Assert
    with pytest.raises(SoupError) as excinfo:
        ArchiveScraper(html_content, html_tag, post_control)

    # Assert that the exception is of type SoupError
    assert isinstance(excinfo.value, SoupError)
    # Check that the error message contains the expected string from the raised exception
    assert "Error initializing a BeautifulSoup object: Mock BeautifulSoup Initialization Error" in str(excinfo.value)
    # Verify that BeautifulSoup was called with the correct arguments
    mock_beautifulsoup.assert_called_once_with(html_content, "html.parser")

def test_archive_to_list_success():
    """Test archive_to_list extracts URLs correctly."""
    # Arrange
    html_content = b"""
    <html>
    <body>
        <div class="post">
            <a href="http://archive.example.com/thread/123" string="Reply">Reply</a>
        </div>
        <div class="post">
            <a href="http://archive.example.com/thread/456" string="Reply">Reply</a>
        </div>
        <div class="other-tag">
            <a href="http://archive.example.com/thread/789" string="Reply">Reply</a>
        </div>
    </body>
    </html>
    """
    html_tag = "div"
    post_control = "Reply"
    scraper = ArchiveScraper(html_content, html_tag, post_control)

    # Act
    urls = scraper.archive_to_list()

    # Assert
    expected_soup = BeautifulSoup(html_content, "html.parser")
    expected_urls = expected_soup.find_all('div')
    expected_urls = [a for div in expected_urls for a in div.find_all('a', href=True, string="Reply")]

    assert [url for url in urls] == [url['href'] for url in expected_urls]

def test_archive_to_list_tag_not_found():
    """Test archive_to_list raises TagNotFoundError when html_tag is missing."""
    # Arrange
    html_content = b"<html><body><div class='other-tag'></div></body></html>"
    html_tag = "section"  # Doesn't exist in the HTML
    post_control = "Reply"
    scraper = ArchiveScraper(html_content, html_tag, post_control)

    # Act & Assert
    with pytest.raises(TagNotFoundError) as excinfo:
        scraper.archive_to_list()

    # Assert that the exception is of type TagNotFoundError
    assert isinstance(excinfo.value, TagNotFoundError)
    assert f"Element with tag '{html_tag}' not found." in str(excinfo.value)

def test_archive_to_list_no_thread_link_found():
    """Test archive_to_list raises NoThreadLinkFoundError when no links with post_control text are found."""
    # Arrange
    html_content = b"""
    <html>
    <body>
        <div class="post">
            <a href="http://archive.example.com/thread/123" string="View">View</a>
        </div>
        <div class="post">
            <p>Blablabla</p>
        </div>
    </body>
    </html>
    """
    html_tag = "div"
    post_control = "Reply"  # Links have "View" text, not "Reply"
    scraper = ArchiveScraper(html_content, html_tag, post_control)

    # Act & Assert
    with pytest.raises(NoThreadLinkFoundError) as excinfo:
        scraper.archive_to_list()

    # Assert that the exception is of type NoThreadLinkFoundError
    assert isinstance(excinfo.value, NoThreadLinkFoundError)
    assert f"URLs with anchor text '{post_control}' not found." in str(excinfo.value)

def test_archive_to_list_handles_tags_with_no_children():
    """Test archive_to_list handles instances of the tag with no child elements."""
    # Arrange
    html_content = b"""
    <html>
    <body>
        <div class="post">
            </div>
        <div class="post">
            <a href="http://archive.example.com/thread/456" string="Reply">Reply</a>
        </div>
    </body>
    </html>
    """
    html_tag = "div"
    post_control = "Reply"
    scraper = ArchiveScraper(html_content, html_tag, post_control)

    # Act
    urls = scraper.archive_to_list()

    # Assert
    # Only the link from the second div should be found
    expected_soup = BeautifulSoup(html_content, "html.parser")
    expected_urls = expected_soup.find_all('div', class_='post')
    expected_urls = [a for div in expected_urls for a in div.find_all('a', href=True, string="Reply")]
    expected_urls = [url for url in expected_urls if '456' in url['href']]  # Filter to the one expected link

    assert [url for url in urls] == [url['href'] for url in expected_urls]