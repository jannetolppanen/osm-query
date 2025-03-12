# test_location_types.py
import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from src.osm_data_fetcher import OSMDataFetcher
import requests

# Fixture for sample location types configuration
@pytest.fixture
def sample_location_types():
    return {
        "church": {
            "description": "Christian places of worship",
            "query_type": "center",
            "tags": [
                {
                    "type": "primary",
                    "conditions": [
                        {"key": "amenity", "value": "place_of_worship"},
                        {"key": "religion", "value": "christian"}
                    ]
                },
                {
                    "type": "building",
                    "conditions": [
                        {"key": "building", "value": "church"}
                    ]
                }
            ]
        },
        "national_park": {
            "description": "National parks and protected areas",
            "query_type": "geom",
            "tags": [
                {
                    "type": "primary",
                    "conditions": [
                        {"key": "boundary", "value": "national_park"}
                    ]
                }
            ]
        }
    }

@pytest.fixture
def sample_country_codes():
    return {
        "NL": "Netherlands",
        "VA": "Vatican City",
        "US": "United States",
        "FR": "France"
    }

@pytest.fixture
def mock_fetcher(tmp_path, sample_country_codes, sample_location_types):
    # Create a temporary config directory
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    # Create a temporary country codes file
    country_codes_file = config_dir / "country_codes.json"
    with open(country_codes_file, 'w') as f:
        json.dump(sample_country_codes, f)
    
    # Create a temporary location types file
    location_types_file = config_dir / "location_types.json"
    with open(location_types_file, 'w') as f:
        json.dump(sample_location_types, f)
    
    # Create and return the fetcher with the temp config path
    return OSMDataFetcher(config_path=str(config_dir))

# Test location types loading
def test_load_location_types(mock_fetcher, sample_location_types):
    assert mock_fetcher.location_types == sample_location_types

# Test getting location type configuration
def test_get_location_type_config(mock_fetcher, sample_location_types):
    # Test existing location type
    church_config = mock_fetcher.get_location_type_config("church")
    assert church_config == sample_location_types["church"]
    
    # Test non-existing location type
    nonexistent_config = mock_fetcher.get_location_type_config("nonexistent")
    assert nonexistent_config is None

# Test tag query building
def test_build_tag_query(mock_fetcher):
    # Test with single condition
    tag_group = {
        "conditions": [
            {"key": "building", "value": "church"}
        ]
    }
    query = mock_fetcher.build_tag_query(tag_group)
    assert query == '["building"="church"]'
    
    # Test with multiple conditions
    tag_group = {
        "conditions": [
            {"key": "amenity", "value": "place_of_worship"},
            {"key": "religion", "value": "christian"}
        ]
    }
    query = mock_fetcher.build_tag_query(tag_group)
    assert query == '["amenity"="place_of_worship"]["religion"="christian"]'

# Test query building for different location types
def test_build_query_for_different_types(mock_fetcher):
    # Test church query
    church_query = mock_fetcher.build_query("FR", "church")
    assert 'area["ISO3166-1"="FR"]' in church_query
    assert '["amenity"="place_of_worship"]["religion"="christian"]' in church_query
    assert '["building"="church"]' in church_query
    assert "out center body;" in church_query
    
    # Test national park query
    park_query = mock_fetcher.build_query("US", "national_park")
    assert 'area["ISO3166-1"="US"]' in park_query
    assert '["boundary"="national_park"]' in park_query
    assert "out geom body;" in park_query
    
    # Test non-existent location type
    nonexistent_query = mock_fetcher.build_query("FR", "nonexistent")
    assert nonexistent_query is None

# Test fetch_data with mocked API response for different location types
@patch('requests.post')
def test_fetch_data_for_different_types(mock_post, mock_fetcher):
    # Create a mock response for churches
    church_response = MagicMock()
    church_response.status_code = 200
    church_response.json.return_value = {
        "elements": [{"id": 1, "tags": {"name": "Notre Dame"}}]
    }
    
    # Create a mock response for national parks
    park_response = MagicMock()
    park_response.status_code = 200
    park_response.json.return_value = {
        "elements": [{"id": 2, "tags": {"name": "Yellowstone"}}]
    }
    
    # Configure the mock to return different responses based on input
    def side_effect(*args, **kwargs):
        if 'church' in kwargs['data']['data']:
            return church_response
        elif 'national_park' in kwargs['data']['data']:
            return park_response
        return None
    
    mock_post.side_effect = side_effect
    
    # Test fetching churches
    church_data, church_country = mock_fetcher.fetch_data("France", "church")
    assert church_country == "FR"
    assert church_data["elements"][0]["tags"]["name"] == "Notre Dame"
    
    # Test fetching national parks
    park_data, park_country = mock_fetcher.fetch_data("United States", "national_park")
    assert park_country == "US"
    assert park_data["elements"][0]["tags"]["name"] == "Yellowstone"
    
    # Test with non-existent location type
    nonexistent_data, nonexistent_country = mock_fetcher.fetch_data("France", "nonexistent")
    assert nonexistent_data is None
    assert nonexistent_country == "FR"
