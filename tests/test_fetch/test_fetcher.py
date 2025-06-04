# Imports
import pytest
import requests

from web_scraper.fetch.fetcher import fetch_html_content, NetworkError

@pytest.fixture
def mock_response(mocker):
    """Fixture to create a mock requests.Response object."""
    mock_resp = mocker.MagicMock(spec=requests.Response)
    # Default successful response
    mock_resp.status_code = 200
    mock_resp.content = b"<html><body>Mock HTML Content</body></html>"
    # Default: raise_for_status does nothing (success)
    mock_resp.raise_for_status.return_value = None  
    return mock_resp

def test_fetch_html_content_success(mocker, mock_response):
    """Test successful fetching of HTML content."""
    # Arrange
    test_url = "http://example.com/page"
    mocker.patch("requests.get", return_value=mock_response)
    
    # Act
    content = fetch_html_content(test_url)

    # Assert
    requests.get.assert_called_once_with(test_url)
    mock_response.raise_for_status.assert_called_once()  # Ensure status is checked
    assert content == b"<html><body>Mock HTML Content</body></html>"

def test_fetch_html_content_http_error(mocker, mock_response):
    """Test fetching handles HTTP errors (4xx, 5xx)."""
    # Arrange
    test_url = "http://example.com/notfound"
    http_error = requests.exceptions.HTTPError("404 Client Error: Not Found for url")
    mock_response.raise_for_status.side_effect = http_error
    mocker.patch("requests.get", return_value=mock_response)

    # Act & Assert
    with pytest.raises(NetworkError) as excinfo:
        fetch_html_content(test_url)

    # Assert
    requests.get.assert_called_once_with(test_url)
    mock_response.raise_for_status.assert_called_once()
    assert isinstance(excinfo.value, NetworkError)
    # Check the original exception is chained
    assert "404 Client Error: Not Found for url" in str(excinfo.value.__cause__) 

def test_fetch_html_content_request_exception(mocker):
    """Test fetching handles other requests.RequestException errors."""
    # Arrange
    test_url = "http://example.com/timeout"
    request_exception = requests.exceptions.RequestException("Connection timed out")
    mocker.patch("requests.get", side_effect=request_exception)

    # Act & Assert
    with pytest.raises(NetworkError) as excinfo:
        fetch_html_content(test_url)

    # Assert
    requests.get.assert_called_once_with(test_url)
    # raise_for_status is not called if requests.get itself raises an exception
    assert isinstance(excinfo.value, NetworkError)
    # Check the original exception is chained
    assert "Connection timed out" in str(excinfo.value.__cause__) 

def test_fetch_html_content_empty_content(mocker, mock_response):
    """Test fetching handles successful response with empty content."""
    # Arrange
    test_url = "http://example.com/empty"
    mock_response.content = b""  # Empty content
    mocker.patch("requests.get", return_value=mock_response)

    # Act
    content = fetch_html_content(test_url)

    # Assert
    requests.get.assert_called_once_with(test_url)
    mock_response.raise_for_status.assert_called_once()
    assert content == b""