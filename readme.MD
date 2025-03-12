# OpenStreetMap Data Fetcher

A flexible tool for fetching different types of location data from OpenStreetMap using the Overpass API.

## Features

- Fetch data for various location types (churches, national parks, museums, etc.)
- Configure search criteria through JSON configuration files
- Command-line interface with argument parsing
- Retry logic for API requests
- Automatic data saving in JSON format
- Comprehensive test suite

## Setup

1. Clone this repository
2. Ensure Python 3.6+ is installed
3. Install required packages:
   ```
   pip install requests pytest
   ```
4. Ensure the config directory contains the required configuration files:
   - `country_codes.json` - ISO country codes and names
   - `location_types.json` - Configuration for different location types

## Usage

### Basic Usage

```bash
# Fetch churches in France (default)
python main.py

# Fetch national parks in the United States
python main.py --country "United States" --type national_park

# List available location types
python main.py --list-types
```

### Command-line Arguments

- `--country`, `-c`: Country name to search within (default: "France")
- `--type`, `-t`: Location type to search for (default: "church")
- `--list-types`, `-l`: List available location types

## Testing

The project includes a comprehensive test suite covering both unit tests and integration tests.

### Running Tests

```bash
# Run tests without API calls
pytest tests/ -v -k "not api_call"

# Run only unit tests
pytest tests/test_osm_fetcher.py tests/test_location_types.py -v

# Run tests that make actual API calls (marked with api_call)
pytest tests/ -v -m api_call

# Run a specific test file
pytest tests/test_location_types.py -v
```

### Test Categories

- **Unit Tests**: Test individual components without making API calls
  - `test_osm_fetcher.py` - Tests for the OSMDataFetcher class
  - `test_location_types.py` - Tests for location type configuration handling

- **Integration Tests**: Test components working together with real API calls
  - `test_integration.py` - Tests the fetcher's API integration
  - `test_end_to_end.py` - Tests the entire system from command-line to file output

### Setting Up Test Markers

To enable the custom test markers, create a `pytest.ini` file in your project root:

```ini
[pytest]
markers =
    api_call: marks tests that make actual API calls
```

## Adding New Location Types

To add a new location type, edit the `config/location_types.json` file and add a new entry with the following structure:

```json
"your_location_type": {
  "description": "Description of the location type",
  "query_type": "center",  // "center" for point features, "geom" for area features
  "tags": [
    {
      "type": "primary",
      "conditions": [
        {"key": "osm_key", "value": "osm_value"}
      ]
    },
    {
      "type": "alternative",
      "conditions": [
        {"key": "another_key", "value": "another_value"}
      ]
    }
  ]
}
```

For example, to include basilicas and cathedrals in the church type:

```json
"church": {
  "description": "Christian places of worship including churches, basilicas and cathedrals",
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
    },
    {
      "type": "building",
      "conditions": [
        {"key": "building", "value": "cathedral"}
      ]
    },
    {
      "type": "building",
      "conditions": [
        {"key": "building", "value": "basilica"}
      ]
    }
  ]
}
```

## Project Structure

- `main.py` - Main script and command-line interface
- `src/`
  - `osm_data_fetcher.py` - Handles fetching data from OpenStreetMap
  - `data_saver.py` - Utility for saving data to files
- `config/`
  - `country_codes.json` - ISO country codes and names
  - `location_types.json` - Configuration for different location types
- `data/` - Directory where fetched data is saved
- `tests/` - Test suite
  - `test_osm_fetcher.py` - Unit tests for the fetcher
  - `test_location_types.py` - Unit tests for location type handling
  - `test_integration.py` - Integration tests with the API
  - `test_end_to_end.py` - End-to-end system tests
  - `test_main_integration.py` - Tests for the main script

## Notes on OpenStreetMap Tags

When configuring new location types, refer to the [OpenStreetMap Wiki](https://wiki.openstreetmap.org/wiki/Map_features) for appropriate tags to use in your queries.

## Future Enhancements

- Support for bounding box and radius filters
- Additional export formats (GeoJSON, CSV, KML)
- Visualization of results with simple web map
- More location types (airports, hospitals, schools, etc.)
