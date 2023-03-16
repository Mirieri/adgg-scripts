import os
import concurrent.futures
import threading

import mysql.connector
import logging
import gzip

logging.basicConfig(level=logging.DEBUG)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "adgg"
}

BACKUP_FOLDER = "/home/user/Desktop/backup_test"
BATCH_SIZE = 5000
COUNTRY_ID = 14

lock = threading.Lock()


def connect_to_db():
    logging.debug("Connecting to database...")
    return mysql.connector.connect(**DB_CONFIG)


def get_table_names(conn):
    logging.debug("Getting table names...")
    cursor = conn.cursor(buffered=True)
    cursor.execute("SHOW TABLES")
    return [row[0] for row in cursor.fetchall()]


def backup_table(table_name):
    logging.debug(f"Backing up table {table_name}...")

    columns_query = f"SHOW COLUMNS FROM {table_name}"
    insert_query = f"INSERT INTO {table_name} VALUES "

    try:
        conn = connect_to_db()
        cursor = conn.cursor(buffered=True)
        cursor.execute(columns_query)
        columns = [column[0] for column in cursor.fetchall()]

        if "country_id" not in columns:
            select_query = f"SELECT * FROM {table_name}"
            cursor.execute(select_query)
            results = cursor.fetchall()

            rows = [tuple(row) for row in results]

        else:
            select_query = f"SELECT * FROM {table_name} WHERE country_id=%s"
            cursor.execute(select_query, (COUNTRY_ID,))
            results = cursor.fetchall()

            rows = [tuple(row) for row in results]

        if not rows:
            logging.warning(f"No data found for table {table_name}")

        else:
            table_file = os.path.join(BACKUP_FOLDER, f"{table_name}.sql.gz")
            with gzip.open(table_file, "at") as f:
                start = 0
                end = min(BATCH_SIZE, len(rows))
                while start < len(rows):
                    batch = rows[start:end]
                    batch_insert = f"{insert_query} {','.join(map(str, batch))};\n"
                    with lock:
                        f.write(batch_insert)
                    start += BATCH_SIZE
                    end = min(end + BATCH_SIZE, len(rows))

    except mysql.connector.errors.PoolError as e:
        logging.exception(f"Error backing up table {table_name}: {str(e)}")
        raise e
    finally:
        conn.close()


def backup_database():
    logging.debug("Backing up database...")
    conn = connect_to_db()

    try:
        table_names = get_table_names(conn)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(backup_table, table_name) for table_name in table_names]

        logging.info("Backup process completed successfully.")

    except mysql.connector.errors.PoolError as e:
        logging.exception(f"Error backing up database: {str(e)}")
        raise e
    finally:
        conn.close()


if __name__ == "__main__":
    backup_database()
