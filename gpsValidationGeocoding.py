import os
from concurrent.futures import ProcessPoolExecutor
from functools import partial
import mysql.connector
import pandas as pd
import googlemaps

# Database connection details
host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")

# Connect to database
try:
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    print("Database connected successfully!")
except Exception as e:
    print(f"Error connecting to the database: {str(e)}")
    exit()

# Google Maps API key
api_key = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=api_key)

# SQL query to fetch GPS coordinates from the table in the database
query = "SELECT id, ROUND(latitude, 5), ROUND(longitude, 5) FROM core_animal WHERE latitude IS NOT NULL"

# Batch size and number of processes to use for parallel processing
batch_size = 1000
num_processes = 4

# Load cached results, if any
cache_file = 'gps_test_results_cache.csv'

if os.path.exists(cache_file):
    cache_df = pd.read_csv(cache_file)
else:
    cache_df = pd.DataFrame(columns=['latitude', 'longitude', 'country'])

# Dictionary to store previously queried GPS coordinates and their corresponding country
results_cache = {}


# Define function to check cache for GPS location
def check_cache(row):
    # Check if GPS location is in cache
    latitude = row['latitude']
    longitude = row['longitude']
    cached_row = cache_df[cache_df[['latitude', 'longitude']].eq([latitude, longitude]).all(axis=1)]
    if not cached_row.empty:
        # Use cached result
        country = cached_row.iloc[0]['country']
        return row['id'], latitude, longitude, country == 'Kenya', country
    else:
        # GPS location not in cache
        return row


# Define function to geocode GPS location
def geocode(row):
    id = row['id']
    latitude = row['latitude']
    longitude = row['longitude']
    try:
        # Check if location has already been queried before
        location_key = f"{latitude},{longitude}"
        if location_key in results_cache:
            # Use previously queried values
            country, test_passed = results_cache[location_key]
        else:
            # Query Google Maps API
            result = gmaps.reverse_geocode((latitude, longitude))
            country = None
            for component in result[0]['address_components']:
                if 'country' in component['types']:
                    country = component['long_name']
                    break
            if country is not None:
                results_cache[location_key] = (country, country == 'Kenya')
            else:
                results_cache[location_key] = (None, False)

        return id, latitude, longitude, results_cache[location_key][1], results_cache[location_key][0]
    except Exception as e:
        # Geocoding failed
        print(f"Geocoding failed for ({latitude}, {longitude}): {str(e)}")
        return None


# Define callback function to update processing count
def update_count(count, lock):
    with lock:
        count.value += 1
        print(f"{count.value}/{num_rows} rows processed", end='\r')


# Get total number of rows to process
with mydb.cursor() as cursor:
    cursor.execute(query)
    num_rows = cursor.rowcount

    # Initialize processing count
    from multiprocessing import Value, Lock

    count = Value('i', 0)
    lock = Lock()

    # Process rows in parallel
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        while True:
            # Fetch rows in batch
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break

            # Apply caching
            rows = list(executor.map(check_cache, rows))

            # Apply geocoding in parallel
            geocode_partial = partial(geocode)
            results = list(executor.map(geocode_partial, rows))

            # Update cache
            new_cache_rows = []
            for result in results:
                if result is not None:
                    id_, latitude, longitude, test_passed, country = result
                    if country is not None:
                        new_cache_rows.append({'latitude': latitude, 'longitude': longitude, 'country': country})
                    update_count(count, lock)
            if new_cache_rows:
                new_cache_df = pd.DataFrame(new_cache_rows)
                cache_df = pd.concat([cache_df, new_cache_df], ignore_index=True)
                cache_df.to_csv(cache_file, index=False)

# Close database connection
mydb.close()
