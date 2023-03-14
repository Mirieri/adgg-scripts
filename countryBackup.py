import os
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

# get database credentials and backup folder from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
BACKUP_FOLDER = os.getenv("BACKUP_FOLDER")
BACKUP_NAME = os.getenv("BACKUP_NAME")

# create backup folder if it doesn't exist
if not os.path.exists(BACKUP_FOLDER):
    os.makedirs(BACKUP_FOLDER)

# set command to execute mysqldump with appropriate options
cmd = f"mysqldump -h {DB_HOST} -u {DB_USER} -p{DB_PASSWORD} \
       --databases {DB_NAME} --single-transaction --quick"

# generate backup file for current table with specified name
filename = f"{BACKUP_FOLDER}/{BACKUP_NAME}.sql"

# Cache result of command before iterating over tables
table_list = os.popen(f"{cmd} -r {filename} --tables").read().split()

for table in table_list:

    # check if country_id column exists in table
    if "country_id" in os.popen(f"{cmd} -r {filename} -t {table} | head -n 1").read():
        # filter data by country_id column
        cmd = f"{cmd} --where=\"country_id = '10'\""

print(f"All done check the backup in the following location {BACKUP_FOLDER}/{BACKUP_NAME}.sql")
