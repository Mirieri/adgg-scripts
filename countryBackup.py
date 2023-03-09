import os

# set variables for database credentials and backup folder
DB_HOST = 'localhost'
DB_USER = 'username'
DB_PASSWORD = 'password'
DB_NAME = 'database_name'
BACKUP_FOLDER = '/path/to/backup/folder'

# create backup folder if it doesn't exist
if not os.path.exists(BACKUP_FOLDER):
    os.makedirs(BACKUP_FOLDER)

# set command to execute mysqldump with appropriate options
cmd = f"mysqldump -h {DB_HOST} -u {DB_USER} -p{DB_PASSWORD} --databases {DB_NAME} --single-transaction --quick"

# iterate over all tables in the database
for table in os.popen(f"{cmd} -r - --tables").read().split():
    # check if country_id column exists in table
    if "country_id" in os.popen(f"{cmd} -r - -t {table} | head -n 1").read():
        # filter data by country_id column
        cmd = f"{cmd} --where=\"country_id = 'USA'\""
    # generate backup file for current table
    filename = f"{BACKUP_FOLDER}/{table}.sql"
    os.system(f"{cmd} {table} > {filename}")
