import time
import json
import requests
from pathlib import Path


class OSMDataFetcher:
    """
    Class to fetch structure data from OpenStreetMap using Overpass API.
    Supports different location types defined in configuration files.
    """
    def __init__(self, config_path="config"):
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.config_path = Path(config_path)
        self.country_codes = self._load_country_codes()
        self.location_types = self._load_location_types()

    def _load_country_codes(self):
        """Load country codes from JSON file."""
        try:
            with open(self.config_path / "country_codes.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("Country codes file not found. Using empty dictionary.")
            return {}

    def _load_location_types(self):
        """Load location types from JSON file."""
        try:
            with open(self.config_path / "location_types.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("Location types file not found. Using default types.")
            return {}

    def get_country_code(self, country_name):
        """Get ISO country code from country name."""
        # Create a reverse mapping of country names to codes
        name_to_code = {name.lower(): code for code, name in self.country_codes.items()}
        return name_to_code.get(country_name.lower())

    def get_location_type_config(self, location_type):
        """Get configuration for a specific location type."""
        config = self.location_types.get(location_type)
        if not config:
            print(f"Warning: Location type '{location_type}' not found in configuration.")
            return None
        return config

    def build_tag_query(self, tag_group):
        """Build a query fragment for a group of tags."""
        query_parts = []
        
        for condition in tag_group["conditions"]:
            key = condition["key"]
            value = condition["value"]
            query_parts.append(f'["{key}"="{value}"]')
            
        return "".join(query_parts)

    def build_query(self, country_code, location_type):
        """Build an Overpass query for the specified country and location type."""
        # Get configuration for the location type
        config = self.get_location_type_config(location_type)
        if not config:
            return None
            
        # Determine output type (center for points, geom for areas)
        output_type = config.get("query_type", "center")
        
        # Start building query
        query = f"""
        [out:json][timeout:300];
        // Query using ISO country code
        area["ISO3166-1"="{country_code}"]->.searchArea;
        // Find locations by type
        ("""
        
        # Add each tag group as a query section
        for tag_group in config["tags"]:
            tag_query = self.build_tag_query(tag_group)
            query += f"""
          node{tag_query}(area.searchArea);
          way{tag_query}(area.searchArea);
          relation{tag_query}(area.searchArea);"""
            
        # Complete the query
        query += f"""
        );
        // Output format
        out {output_type} body;
        """
        
        return query

    def fetch_data(self, country_name, location_type, max_retries=3, initial_delay=10):
        """
        Fetch data from Overpass API with retry logic.
        
        Args:
            country_name (str): Name of the country
            location_type (str): Type of location to search for
            max_retries (int): Maximum number of retry attempts
            initial_delay (int): Initial delay between retries in seconds
            
        Returns:
            tuple: (JSON response or None if failed, country_code)
        """
        # Get country code from name
        country_code = self.get_country_code(country_name)
        if not country_code:
            print(f"Error: Could not find ISO code for country '{country_name}'")
            return None, None
            
        # Build query based on location type
        query = self.build_query(country_code, location_type)
        if not query:
            print(f"Error: Could not build query for location type '{location_type}'")
            return None, country_code
            
        print(f"Fetching {location_type} data from {country_name} ({country_code})...")
        
        retry_delay = initial_delay
        
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt+1}/{max_retries}")
                response = requests.post(
                    self.overpass_url, 
                    data={"data": query}, 
                    timeout=360
                )
                response.raise_for_status()
                
                data = response.json()
                element_count = len(data.get('elements', []))
                print(f"Found {element_count} {location_type} locations")
                
                return data, country_code
            except requests.exceptions.RequestException as e:
                print(f"Error during API request: {e}")
            
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
        
        return None, country_code