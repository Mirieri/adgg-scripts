
from googlemaps.geocoding import geocode


def test_geocoding_mechanism():
    # Lookup GPS coordinates for Nairobi, Kenya
    latitude = -1.2921
    longitude = 36.8219
    input_row = {'id': 1, 'latitude': latitude, 'longitude': longitude}
    output_row = geocode(input_row)

    # Verify output
    assert output_row == (1, latitude, longitude, True, 'Kenya')




