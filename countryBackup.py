import os
import time
import datetime

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database credentials and backup folder from environment variables
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
backup_folder = os.path.abspath(os.getenv("BACKUP_FOLDER"))
backup_name = os.getenv("BACKUP_NAME")

# Set command to execute mysqldump with appropriate options
cmd = f"mysqldump -h {db_host} -u {db_user} -p{db_pass} --databases {db_name} --single-transaction --quick"

# Initialize timestamp variables
start_time = datetime.datetime.now()
end_time = datetime.datetime.now()

# Iterate over all tables in the database
for table in os.popen(f"{cmd} -r - --tables").read().split():
    # Check if country_id column exists in table
    if "country_id" in os.popen(f"{cmd} -r - -t {table} | head -n 1").read():
        # Filter data by country_id column
        cmd = f"{cmd} --where=\"country_id = '10'\""
        
    # Generate backup file for current table with specified name
    filename = f"{backup_folder}/{backup_name}_{table}.sql"
    
    # Update start timestamp for timer
    start_time = datetime.datetime.now()
    
    # Run command to generate backup file
    os.system(f"{cmd} {table} > {filename}")
    
    # Update end timestamp for timer and calculate duration
    end_time = datetime.datetime.now()
    duration = end_time - start_time
    
    # Display countdown
    print(f"Table '{table}' backup completed in {duration.seconds} seconds.")
    time.sleep(1)
    
# Calculate overall duration
overall_duration = end_time - start_time

# Display overall duration
print(f"All tables backed up in {overall_duration.seconds} seconds.")
