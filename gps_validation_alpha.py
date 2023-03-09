import os
import mysql.connector
import pandas as pd
import googlemaps
from functools import partial
from multiprocessing import Pool

# Replace this with your own database connection code
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="adgg"
)

# Replace this with your Google Maps API key
gmaps = googlemaps.Client(key='YOUR_API_KEY')

# Replace this with the name of the table in your database that contains GPS coordinates
cursor = mydb.cursor()
cursor.execute("SELECT id, ROUND(latitude, 5), ROUND(longitude, 5) FROM core_animal WHERE latitude IS NOT NULL")

batch_size = 1000
num_processes = 4

# Load cached results, if any
cache_file = 'gps_test_results_cache.csv'
if os.path.exists(cache_file):
    cache_df = pd.read_csv(cache_file)
else:
    cache_df = pd.DataFrame(columns=['latitude', 'longitude', 'country'])


# Define function to check cache for GPS location
def check_cache(row):
    # Check if GPS location is in cache
    latitude = row['latitude']
    longitude = row['longitude']
    cached_row = cache_df[(cache_df['latitude'] == latitude) & (cache_df['longitude'] == longitude)]
    if not cached_row.empty:
        # Use cached result
        country = cached_row.iloc[0]['country']
        return (row['id'], latitude, longitude, country == 'Kenya', country)
    else:
        # GPS location not in cache
        return row


# Define function to geocode GPS location
def geocode(row):
    id = row['id']
    latitude = row['latitude']
    longitude = row['longitude']
    try:
        # Geocode GPS location using Google Maps API
        result = gmaps.reverse_geocode((latitude, longitude))
        country = None
        for component in result[0]['address_components']:
            if 'country' in component['types']:
                country = component['long_name']
                break
        if country == 'Kenya':
            test_passed = True
        else:
            test_passed = False
        return id, latitude, longitude, test_passed, country
    except:
        # Geocoding failed
        return None


# Get total number of rows to process
num_rows = cursor.rowcount

# Initialize processing count
count = 0


# Define callback function to update processing count

def callback(result, count):
    count += 1
    print(f"{count}/{num_rows} rows processed", end='\r')
    callback(result, count)


# Process rows in parallel
with Pool(num_processes) as pool:
    while True:
        # Fetch rows in batch
        rows = cursor.fetchmany(batch_size)
        if not rows:
            break
        # Apply caching
        rows = [check_cache(row) for row in rows]
        # Apply geocoding in parallel

        results = pool.map(geocode, rows)
        # Update cache
        new_cache_rows = []
        for result in results:
            if result is not None:
                id, latitude, longitude, test_passed, country = result
                if country is not None:
                    new_cache_rows.append({'latitude': latitude, 'longitude': longitude, 'country': country})
                print(
                    f"ID: {id}, Latitude: {latitude}, Longitude: {longitude}, Country: {country}, Test Passed: {test_passed}")
            callback(result)
        if new_cache_rows:
            new_cache_df = pd.DataFrame(new_cache_rows)
            cache_df = pd.concat([cache_df, new_cache_df], ignore_index=True)
            cache_df.to_csv(cache_file, index=False)
