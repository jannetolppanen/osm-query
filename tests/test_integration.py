import pytest
from src.osm_data_fetcher import OSMDataFetcher

# Mark this test to be skipped by default (to avoid actual API calls during regular testing)
@pytest.mark.skip(reason="Makes actual API calls")
def test_vatican_city_integration():
    fetcher = OSMDataFetcher()
    data, country_code = fetcher.fetch_data("Holy See (Vatican City State)", "church")
    
    assert country_code == "VA"
    assert data is not None
    assert "elements" in data
    assert len(data["elements"]) > 0