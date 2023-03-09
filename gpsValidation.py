import googlemaps
import mysql.connector
import pandas as pd
import os
import time

# Replace with your own Google Maps API key
gmaps = googlemaps.Client(key='YOUR_API_KEY')

# Replace with your own MySQL database connection code
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="adgg"
)

# Replace with the name of the table in your database that contains GPS coordinates
cursor = mydb.cursor()  
cursor.execute("SELECT id, ROUND(latitude, 5), ROUND(longitude, 5) FROM core_animal where latitude is not null")

batch_size = 10
results = []
total_records = cursor.rowcount
processed_records = 0

while True:
    rows = cursor.fetchmany(batch_size)
    if not rows:
        break
    for (id, latitude, longitude) in rows:
        try:
            # Reverse geocode the latitude and longitude coordinates
            geocode_result = gmaps.reverse_geocode((latitude, longitude), result_type='country')
            if not geocode_result:
                raise ValueError("No results found")
            # Extract the country from the geocoding result
            country = None
            for component in geocode_result[0]['address_components']:
                if 'country' in component['types']:
                    country = component['long_name']
                    break
            if country is None:
                raise ValueError("Country not found in geocoding result")
            if country == 'Kenya':
                results.append((id, latitude, longitude, True, country))
            elif country == 'Ethiopia':
                results.append((id, latitude, longitude, False, country))
            elif country == 'Tanzania':
                results.append((id, latitude, longitude, False, country))
            processed_records += 1
            print(f"Processed {processed_records}/{total_records} records")
        except Exception as e:
            print(f"Error processing record {id}: {str(e)}")
    # Sleep for a short period to avoid hitting rate limits
    time.sleep(0.5)

df = pd.DataFrame(results, columns=['id', 'latitude', 'longitude', 'test_passed', 'country'])

# Replace with the path where you want to save the report
report_path = os.path.expanduser("~/Desktop/gps_test_results.xlsx")
df.to_excel(report_path, index=False)

print(f"Report saved to {report_path}")
