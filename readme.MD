## Running
`pip install -r requirements.txt` to install dependencies
`python main.py` to run the main script

## Configuration
`config/country_codes_iso.txt` contains the country codes used in the queries. The format is `country_name=country_code`

## Tests
`pytest` or `pytest -v` for verbose output
comment `@pytest.mark.skip(reason="Makes actual API calls")` line in `test_api.py` to run actual API calls 