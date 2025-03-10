import time
import json
import requests
from pathlib import Path

class OSMDataFetcher:
    """
    Class to fetch structure data from OpenStreetMap using Overpass API.
    """
    def __init__(self, config_path="config"):
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.config_path = Path(config_path)
        self.country_codes = self._load_country_codes()

    def _load_country_codes(self):
        """Load country codes from JSON file."""
        try:
            with open(self.config_path / "country_codes.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("Country codes file not found. Using empty dictionary.")
            return {}

    def get_country_code(self, country_name):
        """Get ISO country code from country name."""
        # Create a reverse mapping of country names to codes
        name_to_code = {name.lower(): code for code, name in self.country_codes.items()}
        return name_to_code.get(country_name.lower())

    def build_query(self, country_code, structure_type):
        """Build an Overpass query for the specified country and structure type."""
        return f"""
        [out:json][timeout:300];
        // Query using ISO country code
        area["ISO3166-1"="{country_code}"]->.searchArea;
        // Find structures by type
        (
          node["amenity"="place_of_worship"]["religion"="christian"](area.searchArea);
          way["amenity"="place_of_worship"]["religion"="christian"](area.searchArea);
          relation["amenity"="place_of_worship"]["religion"="christian"](area.searchArea);
        );
        // Include additional building tags
        (
          node["building"="{structure_type}"](area.searchArea);
          way["building"="{structure_type}"](area.searchArea);
          relation["building"="{structure_type}"](area.searchArea);
        );
        // Output as center points with all tags
        out center body;
        """

    def fetch_data(self, country_name, structure_type, max_retries=3, initial_delay=10):
        """
        Fetch data from Overpass API with retry logic.
        
        Args:
            country_name (str): Name of the country
            structure_type (str): Type of structure to search for
            max_retries (int): Maximum number of retry attempts
            initial_delay (int): Initial delay between retries in seconds
            
        Returns:
            dict: JSON response or None if failed
        """
        # Get country code from name
        country_code = self.get_country_code(country_name)
        if not country_code:
            print(f"Error: Could not find ISO code for country '{country_name}'")
            return None
            
        query = self.build_query(country_code, structure_type)
        
        print(f"Fetching {structure_type} data from {country_name} ({country_code})...")
        
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
                print(f"Found {element_count} structures")
                
                if element_count > 0:
                    return data, country_code
                else:
                    print("Received empty result")
            except requests.exceptions.RequestException as e:
                print(f"Error during API request: {e}")
            
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
        
        return None, country_code