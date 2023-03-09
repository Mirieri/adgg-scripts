import pandas as pd

from gpsValidationGeocoding import check_cache


def test_caching_mechanism():
    # Add new row to cache dataframe
    new_row = {'latitude': 1.23456, 'longitude': -7.89012, 'country': 'Kenya'}
    cache_df = pd.DataFrame(columns=['latitude', 'longitude', 'country'])
    cache_df = cache_df.append(new_row, ignore_index=True)

    # Create input row for check_cache function
    input_row = {'id': 1, 'latitude': 1.23456, 'longitude': -7.89012}

    # Call check_cache function
    output_row = check_cache(input_row)

    # Verify output
    assert output_row == (1, 1.23456, -7.89012, True, 'Kenya')