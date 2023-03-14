import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv()

try:
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

    cursor = connection.cursor()

    update_query = """
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

    cursor.execute(update_query)

    connection.commit()
    print("Update successful")

except Error as e:
    print(f"Error: {e}")

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Connection closed")
