import pytest
import json
import os
from pathlib import Path
from src.osm_data_fetcher import OSMDataFetcher

# Mark this test to be skipped by default (to avoid actual API calls during regular testing)
@pytest.mark.api_call
class TestIntegration:
    @pytest.fixture(scope="class")
    def setup_config(self, tmp_path_factory):
        """Set up temporary configuration files for testing."""
        config_dir = tmp_path_factory.mktemp("config")
        
        # Create country_codes.json
        with open(config_dir / "country_codes.json", "w", encoding="utf-8") as f:
            json.dump({
                "VA": "Holy See (Vatican City State)",
                "FR": "France",
                "IT": "Italy",
                "US": "United States"
            }, f)
        
        # Create location_types.json
        with open(config_dir / "location_types.json", "w", encoding="utf-8") as f:
            json.dump({
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
                        },
                        {
                            "type": "alternative",
                            "conditions": [
                                {"key": "leisure", "value": "nature_reserve"},
                                {"key": "protect_class", "value": "2"}
                            ]
                        }
                    ]
                }
            }, f)
        
        return config_dir
    
    def test_vatican_city_integration(self, setup_config):
        """Test fetching churches in Holy See (Vatican City State)."""
        fetcher = OSMDataFetcher(config_path=str(setup_config))
        data, country_code = fetcher.fetch_data("Holy See (Vatican City State)", "church")
        
        assert country_code == "VA"
        assert data is not None
        assert "elements" in data
        assert len(data["elements"]) > 0
    
    def test_us_national_parks_integration(self, setup_config):
        """Test fetching national parks in United States."""
        fetcher = OSMDataFetcher(config_path=str(setup_config))
        data, country_code = fetcher.fetch_data("United States", "national_park")
        
        assert country_code == "US"
        assert data is not None
        assert "elements" in data
        
        # National parks should return data
        assert len(data["elements"]) > 0
        
        # We should find at least one famous national park
        famous_parks = ["Yellowstone", "Yosemite", "Grand Canyon"]
        found_famous_park = False
        
        for element in data["elements"]:
            tags = element.get("tags", {})
            if "name" in tags:
                park_name = tags["name"]
                if any(famous in park_name for famous in famous_parks):
                    found_famous_park = True
                    break
        
        assert found_famous_park, "No famous national parks found in the results"
    
    def test_nonexistent_country_integration(self, setup_config):
        """Test fetching data for a non-existent country."""
        fetcher = OSMDataFetcher(config_path=str(setup_config))
        data, country_code = fetcher.fetch_data("Narnia", "church")
        
        assert country_code is None
        assert data is None
    
    def test_nonexistent_location_type_integration(self, setup_config):
        """Test fetching data for a non-existent location type."""
        fetcher = OSMDataFetcher(config_path=str(setup_config))
        data, country_code = fetcher.fetch_data("France", "unicorn")
        
        assert country_code == "FR"
        assert data is None