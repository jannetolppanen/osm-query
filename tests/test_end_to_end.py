# test_end_to_end.py
import pytest
import os
import json
from pathlib import Path
import subprocess
import shutil

# Mark these tests with our custom marker for API calls
@pytest.mark.api_call
class TestEndToEnd:
    """End-to-end tests for the OSM data fetcher. These tests make actual API calls."""
    
    @pytest.fixture(scope="class")
    def setup_project(self, tmp_path_factory):
        """Set up a temporary project directory with required files."""
        # Create a temp directory for the test
        test_dir = tmp_path_factory.mktemp("test_project")
        
        # Copy necessary files to the temp directory
        # This assumes you're running pytest from the project root
        shutil.copy("main.py", test_dir)
        
        # Create src directory
        src_dir = test_dir / "src"
        src_dir.mkdir()
        shutil.copy("src/osm_data_fetcher.py", src_dir)
        shutil.copy("src/data_saver.py", src_dir)
        
        # Create __init__.py in src directory
        with open(src_dir / "__init__.py", "w") as f:
            pass
        
        # Create config directory
        config_dir = test_dir / "config"
        config_dir.mkdir()
        
        # Create country_codes.json
        with open(config_dir / "country_codes.json", "w", encoding="utf-8") as f:
            json.dump({"VA": "Holy See (Vatican City State)", "FR": "France", "IT": "Italy"}, f)
        
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
                "museum": {
                    "description": "Museums and galleries",
                    "query_type": "center",
                    "tags": [
                        {
                            "type": "primary",
                            "conditions": [
                                {"key": "tourism", "value": "museum"}
                            ]
                        }
                    ]
                }
            }, f)
        
        # Create data directory
        data_dir = test_dir / "data"
        data_dir.mkdir()
        
        return test_dir
    
    def test_vatican_churches(self, setup_project):
        """Test fetching churches in Holy See (Vatican City State)."""
        # Change to the test directory
        original_dir = os.getcwd()
        os.chdir(setup_project)
        
        try:
            # Run the main script
            result = subprocess.run(
                ["python", "main.py", "--country", "Holy See (Vatican City State)", "--type", "church"],
                capture_output=True,
                text=True
            )
            
            # Check if the process completed successfully
            assert result.returncode == 0
            
            # Check if data was fetched
            assert "Found" in result.stdout
            assert "Data saved to" in result.stdout
            
            # Get the output file path from the console output
            output_line = [line for line in result.stdout.split('\n') if "Data saved to" in line][0]
            output_file = output_line.split("Data saved to ")[1]
            
            # Check if the output file exists
            assert os.path.exists(output_file)
            
            # Load and validate the output data
            # Use utf-8 encoding to handle international characters
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if the data has the expected structure
            assert "elements" in data
            assert len(data["elements"]) > 0
            
            # Now check for churches we know are in the data
            found_church = False
            expected_churches = [
                "santa maria", 
                "sant'anna", 
                "santo stefano",
                "grotta di lourdes"
            ]
            
            for element in data["elements"]:
                tags = element.get("tags", {})
                
                # Check name in various languages
                name_fields = ["name", "name:en", "name:it", "alt_name"]
                
                for field in name_fields:
                    if field in tags:
                        name = tags[field].lower()
                        for church in expected_churches:
                            if church.lower() in name:
                                found_church = True
                                print(f"Found expected church: {tags[field]}")
                                break
                
                if found_church:
                    break
            
            # Assert that we found at least one of the expected churches
            assert found_church, "None of the expected churches found in the results"
            
            # Also verify we have the expected number of churches 
            # (matches the 7 from our example data)
            assert len(data["elements"]) >= 12, "Expected at least 12 churches in Vatican"
            
        finally:
            # Change back to the original directory
            os.chdir(original_dir)
    
    def test_italy_museums(self, setup_project):
        """Test fetching museums in Italy."""
        # Change to the test directory
        original_dir = os.getcwd()
        os.chdir(setup_project)
        
        try:
            # Run the main script
            result = subprocess.run(
                ["python", "main.py", "--country", "Italy", "--type", "museum"],
                capture_output=True,
                text=True
            )
            
            # Check if the process completed successfully
            assert result.returncode == 0
            
            # Check if data was fetched
            assert "Found" in result.stdout
            assert "Data saved to" in result.stdout
            
            # Get the output file path from the console output
            output_line = [line for line in result.stdout.split('\n') if "Data saved to" in line][0]
            output_file = output_line.split("Data saved to ")[1]
            
            # Check if the output file exists
            assert os.path.exists(output_file)
            
            # Load and validate the output data
            # Use utf-8 encoding to handle international characters
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if the data has the expected structure
            assert "elements" in data
            assert len(data["elements"]) > 0
            
            # Italy should have many museums, so there should be a good number of results
            assert len(data["elements"]) > 10, "Expected at least 10 museums in Italy"
            
        finally:
            # Change back to the original directory
            os.chdir(original_dir)
    
    def test_list_types(self, setup_project):
        """Test listing available location types."""
        # Change to the test directory
        original_dir = os.getcwd()
        os.chdir(setup_project)
        
        try:
            # Run the main script with --list-types flag
            result = subprocess.run(
                ["python", "main.py", "--list-types"],
                capture_output=True,
                text=True
            )
            
            # Check if the process completed successfully
            assert result.returncode == 0
            
            # Check if the output contains our location types
            assert "church: Christian places of worship" in result.stdout
            assert "museum: Museums and galleries" in result.stdout
            
        finally:
            # Change back to the original directory
            os.chdir(original_dir)