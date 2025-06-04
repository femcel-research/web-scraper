
# Imports
import pytest

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from web_scraper.scrape.homepage_scraper import (
    HomepageScraper,
    SoupError,
    ContainerNotFoundError,
    NoListItemsFoundError,
)

def test_homepage_scraper_init_success():
    """Test successful initialization of HomepageScraper with valid HTML."""
    # Arrange
    html_content = b"<html><body><div class='box right'></div></body></html>"
    url = "http://example.com"
    container = "box right"

    # Act
    scraper = HomepageScraper(html_content, url, container)

    # Assert
    assert isinstance(scraper.soup, BeautifulSoup)
    assert scraper.domain_param == url
    assert scraper.container_param == container

def test_homepage_scraper_init_soup_error(mocker):
    """Test __init__ raises SoupError for invalid HTML content."""
    # Arrange
    mock_beautifulsoup = mocker.patch(
        "web_scraper.scrape.homepage_scraper.BeautifulSoup")
    mock_beautifulsoup.side_effect = Exception(
        "Mock BeautifulSoup Initialization Error")

    html_content = b"<html><body<div class='box right'></body></html>"
    url = "http://example.com"
    container = "box right"

    # Act & Assert
    with pytest.raises(SoupError) as excinfo:
        HomepageScraper(html_content, url, container)

    # Assert that the exception is of type SoupError
    assert isinstance(excinfo.value, SoupError)
    # Check that the error message contains the expected string from the raised exception
    assert "Error initializing a BeautifulSoup object: Mock BeautifulSoup Initialization Error" in str(excinfo.value)
    # Verify that BeautifulSoup was called with the correct arguments
    mock_beautifulsoup.assert_called_once_with(html_content, "html.parser")

def test_homepage_to_list_success_with_relative_links():
    """Test homepage_to_list extracts relative URLs correctly."""
    # Arrange
    html_content = b"""
    <html>
    <body>
        <div class="box right">
            <ul>
                <li><a href="/thread/123">Thread 1</a></li>
                <li><a href="/thread/456">Thread 2</a></li>
            </ul>
        </div>
    </body>
    </html>
    """
    url = "http://example.com"
    container = "box right"
    scraper = HomepageScraper(html_content, url, container)

    # Act
    urls = scraper.homepage_to_list()

    # Assert
    expected_urls = [
        urljoin(url, "/thread/123"),
        urljoin(url, "/thread/456"),
    ]
    assert urls == expected_urls

def test_homepage_to_list_container_not_found():
    """Test homepage_to_list raises ContainerNotFoundError when container is missing."""
    # Arrange
    html_content = b"<html><body><div class='other-box'><ul><li><a href='/a'>Link</a></li></ul></div></body></html>"
    url = "http://example.com"
    container = "box right"  # This class does not exist in the HTML
    scraper = HomepageScraper(html_content, url, container)

    # Act & Assert
    with pytest.raises(ContainerNotFoundError) as excinfo:
        scraper.homepage_to_list()

    # Assert that the exception is of type ContainerNotFoundError
    assert isinstance(excinfo.value, ContainerNotFoundError)
    assert f"Container with class '{container}' not found." in str(excinfo.value)


def test_homepage_to_list_no_list_items_in_container():
    """Test homepage_to_list raises NoListItemsFoundError when container has no list items."""
    # Arrange
    html_content = b"<html><body><div class='box right'><p>Some text but no list.</p></div></body></html>"
    url = "http://example.com"
    container = "box right"
    scraper = HomepageScraper(html_content, url, container)

    # Act & Assert
    with pytest.raises(NoListItemsFoundError) as excinfo:
        scraper.homepage_to_list()

    # Assert that the exception is of type NoListItemsFoundError
    assert isinstance(excinfo.value, NoListItemsFoundError)
    assert f"No list items found within the container '{container}'." in str(excinfo.value)


# TODO: Implement different behavior in the case of empty url_list
# TODO: Use a NoListItemsFound error?
# def test_homepage_to_list_list_items_without_anchor_tags():
#     """Test homepage_to_list returns empty list when list items have no anchor tags."""
#     # Arrange
#     html_content = b"""
#     <html>
#     <body>
#         <div class="box right">
#             <ul>
#                 <li>Just text 1</li>
#                 <li>Just text 2</li>
#             </ul>
#         </div>
#     </body>
#     </html>
#     """
#     url = "http://example.com"
#     container = "box right"
#     scraper = HomepageScraper(html_content, url, container)

#     # Act
#     urls = scraper.homepage_to_list()

#     # Assert
#     assert urls == []  # No links found, so empty list is expected


def test_homepage_to_list_anchor_tags_without_href():
    """Test homepage_to_list ignores anchor tags missing the href attribute."""
    # Arrange
    html_content = b"""
    <html>
    <body>
        <div class="box right">
            <ul>
                <li><a name="link1">Link with no href</a></li>
                <li><a href="/validlink">Valid Link</a></li>
            </ul>
        </div>
    </body>
    </html>
    """
    url = "http://example.com"
    container = "box right"
    scraper = HomepageScraper(html_content, url, container)

    # Act
    urls = scraper.homepage_to_list()

    # Assert
    # Only the link with a valid href should be included
    expected_urls = [urljoin(url, "/validlink")]
    assert urls == expected_urls

def test_homepage_to_list_empty_href():
    """Test homepage_to_list ignores anchor tags with empty href attributes."""
    # Arrange
    html_content = b"""
    <html>
    <body>
        <div class="box right">
            <ul>
                <li><a href="">Empty href link</a></li>
                <li><a href="/validlink">Valid Link</a></li>
            </ul>
        </div>
    </body>
    </html>
    """
    url = "http://example.com"
    container = "box right"
    scraper = HomepageScraper(html_content, url, container)

    # Act
    urls = scraper.homepage_to_list()

    # Assert
    # Only the link with a non-empty href should be included
    expected_urls = [urljoin(url, "/validlink")]
    assert urls == expected_urls

def test_homepage_to_list_container_with_no_children():
    """Test homepage_to_list handles container with no children elements."""
    # Arrange
    html_content = b"""
    <html>
    <body>
        <div class="box right">
        </div>
    </body>
    </html>
    """
    domain_prefix = "http://example.com"
    container = "box right"
    scraper = HomepageScraper(html_content, domain_prefix, container)

    # Act & Assert
    with pytest.raises(NoListItemsFoundError) as excinfo:
        scraper.homepage_to_list()

    # Assert that the exception is of type NoListItemsFoundError
    assert isinstance(excinfo.value, NoListItemsFoundError)
    assert f"No list items found within the container '{container}'." in str(excinfo.value)
