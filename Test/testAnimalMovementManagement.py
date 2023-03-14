import unittest
from unittest.mock import patch
import io
import os
import mysql.connector
import pytest
from dotenv import load_dotenv
from animalMovementManagement import send_email_with_report, execute_update_query, connect_to_db


class TestAnimalDataUpdater(unittest.TestCase):

    def test_send_email_with_report(self):
        with patch('builtins.open', create=True) as mock_open, \
                patch('smtplib.SMTP', autospec=True) as mock_smtp:
            mock_open.return_value = io.StringIO(
                "Animal ID,Farm ID,New Farm ID,Region ID,District ID,Ward ID,Village ID\n1,123,456,7,8,9,10")
            send_email_with_report()
            self.assertTrue(mock_smtp.called)
            _, call_kwargs = mock_smtp.mock_calls[0]
            msg = call_kwargs['msg']
            attachments = [part.get_filename() for part in msg.walk() if part.get_filename()]
            self.assertIn('updated_records.csv', attachments)
            self.assertEqual(msg['From'], 'adgg@gmail.com')
            self.assertEqual(msg['To'], 'd.mogaka@cgiar.org')
            self.assertEqual(msg['Subject'], 'Updated Records')

    def test_execute_update_query(self):
        # Connect to the test database
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )

        # Insert test data
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO core_farm (id, region_id, district_id, ward_id, village_id) VALUES ('001', '1001', '2001', '3001', '4001')")
        cur.execute(
            "INSERT INTO core_animal (id, farm_id, region_id, district_id, ward_id, village_id) VALUES ('001', '002', NULL, NULL, NULL, NULL)")
        cur.execute(
            "INSERT INTO core_animal_event (id, event_type, animal_id, additional_attributes) VALUES (1, 9, '001', '{\"557\":\"001\"}')")

        # Call the function being tested
        execute_update_query()

        # Check that the update was successful
        cur.execute("SELECT * FROM core_animal WHERE id = '001'")
        result = cur.fetchone()
        assert result[1] == '001'
        assert result[2] == '1001'
        assert result[3] == '2001'
        assert result[4] == '3001'
        assert result[5] == '4001'

        # Clean up the test data
        cur.execute("DELETE FROM core_animal_event WHERE id = 1")
        cur.execute("DELETE FROM core_animal WHERE id = '001'")
        cur.execute("DELETE FROM core_farm WHERE id = '001'")

        # Commit the changes and close the cursor and connection
        conn.commit()
        cur.close()
        conn.close()


if __name__ == '__main__':
    unittest.main()
