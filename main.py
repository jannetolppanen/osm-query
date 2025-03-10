import json
from pathlib import Path
from src.data_saver import DataSaver
from src.osm_data_fetcher import OSMDataFetcher

def main():
    # Create config directory if it doesn't exist
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)

    # Check if country_codes.json exists
    country_codes_file = config_dir / "country_codes.json"
    if not country_codes_file.exists():
        print(f"Error: {country_codes_file} does not exist. Please create this file with appropriate country codes.")
    
    # Initialize fetcher
    fetcher = OSMDataFetcher()
    
    # Set parameters
    country_name = "Italy"  # Using country name instead of code
    structure_type = "church"
    
    # Fetch data
    osm_data = fetcher.fetch_data(country_name, structure_type)
    
    # Save data if fetch was successful
    if osm_data:
        output_file = f"data/{country_name.lower()}_{structure_type}_length_{len(osm_data[0]['elements'])}.json"
        DataSaver.save_json(osm_data[0], output_file)
    else:
        print("Failed to fetch data after all retry attempts")

if __name__ == "__main__":
    main()