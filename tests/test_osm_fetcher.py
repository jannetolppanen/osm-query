# test_osm_fetcher.py
import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.osm_data_fetcher import OSMDataFetcher
import requests
from requests.exceptions import RequestException


# Fixture for test data
@pytest.fixture
def sample_country_codes():
    return {
        "NL": "Netherlands",
        "VA": "Vatican City",
        "US": "United States"
    }

@pytest.fixture
def mock_fetcher(tmp_path, sample_country_codes):
    # Create a temporary config directory
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    # Create a temporary country codes file
    country_codes_file = config_dir / "country_codes.json"
    with open(country_codes_file, 'w') as f:
        json.dump(sample_country_codes, f)
    
    # Create and return the fetcher with the temp config path
    return OSMDataFetcher(config_path=str(config_dir))

# Test country code loading
def test_load_country_codes(mock_fetcher, sample_country_codes):
    assert mock_fetcher.country_codes == sample_country_codes

# Test getting country code from name
def test_get_country_code(mock_fetcher):
    assert mock_fetcher.get_country_code("Netherlands") == "NL"
    assert mock_fetcher.get_country_code("netherlands") == "NL"  # Test case insensitivity
    assert mock_fetcher.get_country_code("Nonexistent Country") is None

# Test query building
def test_build_query(mock_fetcher):
    query = mock_fetcher.build_query("NL", "church")
    assert "area[\"ISO3166-1\"=\"NL\"]" in query
    assert "node[\"building\"=\"church\"]" in query

# Test fetch_data with mocked API response
@patch('requests.post')
def test_fetch_data_success(mock_post, mock_fetcher):
    # Create a mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "elements": [{"id": 1, "tags": {"name": "Test Church"}}]
    }
    mock_post.return_value = mock_response
    
    # Call fetch_data
    data, country_code = mock_fetcher.fetch_data("Netherlands", "church")
    
    # Assert results
    assert country_code == "NL"
    assert len(data["elements"]) == 1
    assert data["elements"][0]["id"] == 1
    
    # Assert the API was called with expected parameters
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert "NL" in call_args[1]["data"]["data"]

# Test fetch_data with error
@patch('requests.post')
def test_fetch_data_error(mock_post, mock_fetcher):
    # Mock a request exception
    from requests.exceptions import RequestException
    mock_post.side_effect = RequestException("API Error")
    
    # Call fetch_data
    data, country_code = mock_fetcher.fetch_data("Netherlands", "church", max_retries=1)
    
    # Assert results
    assert data is None
    assert country_code == "NL"