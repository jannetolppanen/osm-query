import json
import argparse
from pathlib import Path
from src.data_saver import DataSaver
from src.osm_data_fetcher import OSMDataFetcher

def list_available_location_types(config_dir):
    """Print available location types from configuration."""
    location_types_file = config_dir / "location_types.json"
    try:
        with open(location_types_file, "r") as f:
            location_types = json.load(f)
            print("\nAvailable location types:")
            for loc_type, config in location_types.items():
                print(f"  - {loc_type}: {config.get('description', '')}")
            print()
    except FileNotFoundError:
        print(f"Error: {location_types_file} does not exist.")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Fetch OSM data for different location types")
    parser.add_argument("--country", "-c", default="Holy See (Vatican City State)", help="Country name to search within")
    parser.add_argument("--type", "-t", default="church", help="Location type to search for")
    parser.add_argument("--list-types", "-l", action="store_true", help="List available location types")
    args = parser.parse_args()
    
    # Create config directory if it doesn't exist
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)

    # Handle list-types command
    if args.list_types:
        list_available_location_types(config_dir)
        return

    # Check if required configuration files exist
    country_codes_file = config_dir / "country_codes.json"
    location_types_file = config_dir / "location_types.json"
    
    if not country_codes_file.exists():
        print(f"Error: {country_codes_file} does not exist. Please create this file with appropriate country codes.")
        return
        
    if not location_types_file.exists():
        print(f"Error: {location_types_file} does not exist. Please create this file with location type definitions.")
        return
    
    # Initialize fetcher
    fetcher = OSMDataFetcher()
    
    # Set parameters from arguments
    country_name = args.country
    location_type = args.type
    
    # Fetch data
    osm_data, country_code = fetcher.fetch_data(country_name, location_type)
    
    # Save data if fetch was successful
    if osm_data:
        element_count = len(osm_data.get('elements', []))
        output_file = f"data/{country_name.lower()}_{location_type}_{element_count}_elements.json"
        DataSaver.save_json(osm_data, output_file)
    else:
        print("Failed to fetch data after all retry attempts")

if __name__ == "__main__":
    main()