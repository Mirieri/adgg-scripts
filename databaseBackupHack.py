import subprocess
import os

# Get the password from the environment variable
# Run the following command to set the password on console export
#   1. MYSQL_PASSWORD_SOURCE_DATABASE=<Your Password> AND
#   2.MYSQL_PASSWORD_DESTINATION_DATABASE=<Your Password>
password = os.environ.get('MYSQL_PASSWORD_SOURCE_DATABASE')

# Destination database
password2 = os.environ.get('MYSQL_PASSWORD_DESTINATION_DATABASE')

# Run the first mysqldump command and capture its output
dump1 = subprocess.Popen(
    ["mysqldump", "-u", "root", "-p", password, "--databases", "adgg", "--tables", "core_animal", "core_farm",
     "core_animal_herd", "core_animal_event", "core_excel_import", "--where=country_id=15"], stdout=subprocess.PIPE)
output1, _ = dump1.communicate()

# Run the second mysqldump command and capture its output
dump2 = subprocess.Popen(
    ["mysqldump", "-u", "root", "-p", password, "--databases", "adgg", "--ignore-table", "adgg.core_animal",
     "--ignore-table", "adgg.core_excel_import", "--ignore-table", "adgg.core_farm", "--ignore-table", "adgg.core_herd",
     "--ignore-table", "adgg.core_animal_event"], stdout=subprocess.PIPE)
output2, _ = dump2.communicate()

# Combine the output of the two commands into one SQL file
backup_sql = output1 + output2

# Write the combined output to a backup file
with open("combined_backup.sql", "wb") as f:
    f.write(backup_sql)

# Create and import into adgg_uganda database
subprocess.run(["mysql", "-u", "root", "-p", password2, "-e", "CREATE DATABASE IF NOT EXISTS adgg_uganda"])
subprocess.run(["mysql", "-u", "root", "-p", password2, "adgg_uganda < combined_backup.sql"])

# Delete the SQL backup file
subprocess.run(["rm", "combined_backup.sql"])
