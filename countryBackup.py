import os
from dotenv import load_dotenv

load_dotenv()

# prompt user for database credentials and backup folder
DB_HOST = input("Enter database host: ")
DB_USER = input("Enter database user: ")
DB_PASSWORD = input("Enter database password: ")
DB_NAME = input("Enter database name: ")
BACKUP_FOLDER = input("Enter backup folder path: ")
BACKUP_NAME = input("Enter backup file name: ")

# create backup folder if it doesn't exist
if not os.path.exists(BACKUP_FOLDER):
    os.makedirs(BACKUP_FOLDER)

# set command to execute mysqldump with appropriate options
cmd = f"mysqldump -h {DB_HOST} -u {DB_USER} -p{DB_PASSWORD} \
       --databases {DB_NAME} --single-transaction --quick"

# generate backup file for current table with specified name
filename = f"{BACKUP_FOLDER}/{BACKUP_NAME}.sql"

# get country_id from user input
country_id = input("Enter country ID to filter by: ")

# Cache result of command before iterating over tables
table_list = os.popen(f"{cmd} -r {filename} --tables").read().split()

for table in table_list:
    # check if country_id column exists in table
    if "country_id" in os.popen(f"{cmd} -r {filename} -t {table} | head -n 1").read():
        # filter data by country_id column
        cmd = f"{cmd} --where=\"country_id = '{country_id}'\""

# execute final command to generate backup file
os.system(f"{cmd} > {filename}")

print(f"All done! Check the backup in the following location: {BACKUP_FOLDER}/{BACKUP_NAME}.sql")
