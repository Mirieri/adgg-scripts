import psycopg2
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Connect to the database using mysql credentials from .env file
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)

# Create a cursor object to execute queries
cur = conn.cursor()

# Execute the SQL query
query = """
    UPDATE
      core_animal
    INNER JOIN core_animal_event ON core_animal.id = core_animal_event.animal_id
    INNER JOIN core_farm ON REPLACE(IFNULL(JSON_EXTRACT(core_animal_event.additional_attributes, '$."557"'), ''), '"', '') = core_farm.id
    SET
      core_animal.farm_id = REPLACE(IFNULL(JSON_EXTRACT(core_animal_event.additional_attributes, '$."557"'), ''), '"', ''),
      core_animal.region_id = core_farm.region_id,
      core_animal.district_id = core_farm.district_id,
      core_animal.ward_id = core_farm.ward_id,
      core_animal.village_id = core_farm.village_id,
      core_animal.updated_at = now()
    WHERE
      event_type = 9;
"""

cur.execute(query)

# Commit the changes
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()
