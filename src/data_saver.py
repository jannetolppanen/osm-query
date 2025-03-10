import json
from pathlib import Path

class DataSaver:
    """Class to handle saving data to various formats."""
    
    @staticmethod
    def save_json(data, filename):
        """Save data to a JSON file."""
        output_path = Path(filename)
        
        # Create directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save data to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Data saved to {output_path}")
        return output_path