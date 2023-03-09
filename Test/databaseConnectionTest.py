import mysql.connector


def test_database_connection():
    # Replace this with your own database connection code
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="adgg"
    )

    # Retrieve GPS coordinates from database
    cursor = mydb.cursor()
    cursor.execute("SELECT id, ROUND(latitude, 5), ROUND(longitude, 5) FROM core_animal WHERE latitude IS NOT NULL")
    num_rows = len(cursor.fetchall())

    # Verify number of rows returned
    assert num_rows == 100  # replace with expected number of rows
