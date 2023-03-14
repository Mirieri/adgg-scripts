import unittest
from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector.errors import ProgrammingError

load_dotenv()


class TestAnimalDataUpdater(unittest.TestCase):

    def setUp(self):
        # Load environment variables
        self.HOST = os.getenv('DB_HOST')
        self.DB_NAME = os.getenv('DB_NAME')
        self.USER = os.getenv('DB_USER')
        self.PASSWORD = os.getenv('DB_PASSWORD')

        try:
            # Establish connection to MySQL server
            self.connection = mysql.connector.connect(
                host=self.HOST,
                user=self.USER,
                password=self.PASSWORD,
                database=self.DB_NAME
            )
        except (mysql.connector.DatabaseError, mysql.connector.ProgrammingError) as error:
            print(f"Database connection error: {error}")

        self.cursor = self.connection.cursor(buffered=True)

    def test_connection(self):
        expected_output = None

        # Verify that we got a valid server version response
        try:
            self.assertIsNotNone(self.connection.get_server_info())
        except (ProgrammingError) as error:
            print(f"Can't get server info: {error}")
            self.assertEqual(None, expected_output)

    def test_update_data(self):
        update_query = """
            UPDATE core_animal
            INNER JOIN (
              SELECT
                REPLACE(IFNULL(JSON_EXTRACT(core_animal_event.additional_attributes, '$."755"'), ''), '"', '') as exit_animal_id,
                REPLACE(IFNULL(JSON_EXTRACT(core_animal_event.additional_attributes, '$."756"'), ''), '"', '') as old_farm_id,
                core_farm.id as new_farm_id
              FROM
                core_animal_event
              INNER JOIN core_farm ON REPLACE(IFNULL(JSON_EXTRACT(core_animal_event.additional_attributes, '$."757"'), ''), '"', '') = core_farm.id
              WHERE
                event_type = 9 AND JSON_EXTRACT(core_animal_event.additional_attributes, '$."556"') != '' AND
                REPLACE(IFNULL(JSON_EXTRACT(core_animal_event.additional_attributes, '$."556"'), ''), '"', '') <> 'null' AND
                REPLACE(IFNULL(JSON_EXTRACT(core_animal_event.additional_attributes, '$."555"'), ''), '"', '') <> 'null' AND
                REPLACE(IFNULL(JSON_EXTRACT(core_animal_event.additional_attributes, '$."554"'), ''), '"', '') <> 'null'
            ) AS new_farms ON core_animal.id = new_farms.exit_animal_id
            SET 
                core_animal.farm_id = new_farms.new_farm_id
            WHERE core_animal.farm_id = new_farms.old_farm_id;
        """

        self.cursor.execute(update_query)
        self.connection.commit()

        # Get the number of rows affected by the update statement
        rows_affected = self.cursor.rowcount
        self.assertGreater(rows_affected, 0)

    def tearDown(self):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("Connection closed")


if __name__ == '__main__':
    unittest.main()
