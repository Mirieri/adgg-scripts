import os
import time
import datetime

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
cmd = f"mysqldump -h {DB_HOST} -u {DB_USER} -p{DB_PASSWORD} --databases {DB_NAME} --single-transaction --quick"
filename = f"{BACKUP_FOLDER}/{BACKUP_NAME}.sql"

# initialize timestamp variables
start_time = datetime.datetime.now()
end_time = datetime.datetime.now()

# generate backup file
os.system(f"{cmd} > {filename}")

# update end timestamp for timer and calculate duration
duration = end_time - start_time

# # display countdown
# print(f"All databases backed up in {duration.seconds} seconds.")

# iterate over all tables in the database
for table in os.popen(f"{cmd} -r - --tables").read().split():
    
    # check if country_id column exists in table
    if "country_id" in os.popen(f"{cmd} -r - -t {table} | head -n 1").read():
        # filter data by country_id column
        cmd = f"{cmd} --where=\"country_id = '10'\""
        
    # generate backup file for current table with specified name
    table_filename = f"{BACKUP_FOLDER}/{BACKUP_NAME}_{table}.sql"
    
    # run command to generate backup file
    os.system(f"{cmd} {table} > {table_filename}")
    
    # update end timestamp for timer and calculate duration
    end_time = datetime.datetime.now()
    duration = end_time - start_time
    
    # print location of backup file on console
    print(f"Backup file for '{table}' is stored in '{table_filename}'")
    
    # # copy the result of the export to backup_name
    # os.system(f"cp {table_filename} {BACKUP_FOLDER}/{BACKUP_NAME}_{table}.sql")
    
    # include mv - BACKUP_NAME.sql after creating a backup file
    os.system(f"mv {filename} {BACKUP_FOLDER}/{BACKUP_NAME}.sql")

    # display countdown
    print(f"Backup for table '{table}' completed in {duration.seconds} seconds.")
    
# calculate overall duration
overall_duration = end_time - start_time

# display overall duration
print(f"All backups are completed in {overall_duration.seconds} seconds.")
