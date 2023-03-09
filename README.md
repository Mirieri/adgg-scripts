
# Description

Playground data processing scripts

<details>
  <summary>Script for MySQL Database Backup</summary> 

This script uses the `os` library to create a MySQL database backup by executing the `mysqldump` command with appropriate options.

### Variables

-   `DB_HOST`: The host name or IP address of the MySQL server.
-   `DB_USER`: The username for the MySQL account.
-   `DB_PASSWORD`: The password for the MySQL account.
-   `DB_NAME`: The name of the database to be backed up.
-   `BACKUP_FOLDER`: The path to the backup folder where the backup files will be stored.

### Process

-   The script checks if the backup folder exists, and creates it if it does not.
-   The `mysqldump` command is set with the appropriate options to execute a backup of the specified database.
-   The script iterates over all tables in the database.
-   For each table, the script checks if the `country_id` column exists in the table.
-   If the column exists, the script filters the data by `country_id` column for the backup.
-   A backup file is generated for the current table in the specified backup folder.

Note that the script assumes that the `mysqldump` command is in the system path. If it is not, the full path to the `mysqldump` command must be specified.
</details>

<details>
  <summary>GPS Validation</summary> 

This script creates a backup of a MySQL database and saves it to a specified folder. It uses the `os` module to interact with the operating system and execute command-line commands.

## Prerequisites

-   MySQL installed on your machine
-   Python 3.x installed on your machine
-   `os` module is available in your Python environment

## Usage

1.  Open the Python script in your preferred editor.
2.  Modify the following variables to match your database credentials and backup folder:

pythonCopy code

`DB_HOST = 'localhost'
DB_USER = 'username'
DB_PASSWORD = 'password'
DB_NAME = 'database_name'
BACKUP_FOLDER = '/path/to/backup/folder'` 

3.  Save the changes.
4.  Open a terminal window and navigate to the directory containing the script.
5.  Run the script using the following command:

bashCopy code

`python backup_mysql.py` 

6.  The script will create a backup of the database and save it to the specified backup folder.

## How It Works

The script uses the `os` module to execute command-line commands. The following steps are taken:

1.  The script checks if the backup folder specified in the `BACKUP_FOLDER` variable exists. If it doesn't exist, the script creates the folder using the `os.makedirs()` function.
    
2.  The script creates a command string to execute the `mysqldump` utility with appropriate options. The command includes the following options:
    
    -   `-h`: Specifies the host name or IP address of the MySQL server
    -   `-u`: Specifies the username to use when connecting to the MySQL server
    -   `-p`: Specifies the password to use when connecting to the MySQL server
    -   `--databases`: Specifies the database to back up
    -   `--single-transaction`: Ensures a consistent backup by using a single transaction
    -   `--quick`: Ensures a faster backup by retrieving rows one at a time
    -   `-r -`: Redirects the output to stdout so that it can be piped to another command
3.  The script uses the `os.popen()` function to execute the command and read the output. The output is split into a list of table names.
    
4.  The script iterates over the list of table names and checks if the table has a `country_id` column. If it does, the script modifies the `mysqldump` command to filter the data by the `country_id` column using the `--where` option.
    
5.  The script generates a backup filename for the current table and executes the modified `mysqldump` command to save the backup to the specified backup folder.
    
6.  The script repeats steps 4 and 5 for each table in the database.
    

## Notes

-   This script is designed to be run on a Unix-like operating system, such as Linux or macOS. It may not work as expected on Windows.
-   You should make sure to keep your backup files in a secure location, as they contain sensitive data.
-   You can modify the script to back up multiple databases by changing the `DB_NAME` variable to a comma-separated list of database names.
</details>

<details>
  <summary>GPS Geocoding Script</summary>

This script is designed to geocode GPS coordinates stored in a MySQL database using the Google Maps API. The script uses the `mysql.connector` library to connect to the database and the `googlemaps` library to access the API. The geocoding is performed in parallel using the `multiprocessing` library, and the results are cached in a CSV file to speed up future lookups.

## Requirements

This script requires the following libraries to be installed:

-   `mysql.connector`
-   `pandas`
-   `googlemaps`

In addition, you will need a Google Maps API key to use the geocoding functionality. You can obtain an API key from the [Google Cloud Console](https://console.cloud.google.com/).

## Usage

To use this script, you will need to replace the following placeholders in the code:

-   `YOUR_API_KEY`: Replace this with your own Google Maps API key
-   `adgg`: Replace this with the name of the database containing the GPS coordinates
-   `core_animal`: Replace this with the name of the table containing the GPS coordinates
-   `root`: Replace this with the username for your MySQL database
-   `batch_size`: Change this to control the number of rows processed in each batch
-   `num_processes`: Change this to control the number of parallel processes used for geocoding
-   `cache_file`: Replace this with the path to the CSV file used to cache geocoding results

Once you have made these changes, you can run the script using the following command:

pythonCopy code

`python gps_geocoding.py` 

The script will output progress information to the console as it processes each batch of rows. Once the script has finished, the cached results will be stored in the CSV file specified in `cache_file`.

## Note

It is recommended to use this script only for small to medium sized datasets. Large datasets may cause performance issues due to the limitations of the Google Maps API free tier. Additionally, using the API for large datasets may result in additional charges from Google.

</details>


<details>
  <summary>Airflow DAG for performing backups</summary>

This is an example DAG (Directed Acyclic Graph) for performing backups using Airflow, a platform to programmatically author, schedule, and monitor workflows.

## Prerequisites

Make sure you have Airflow installed and configured properly. You also need the following Python modules:

-   `datetime`
-   `timedelta`

## DAG details

This DAG is called `backup_dag` and is set to run once a day using the `schedule_interval` parameter. The DAG consists of one task:

-   `backup_script`: This task runs a Bash script to perform the backup. The script is located at `/var/backup_ILRI/DAG_adgg/backup.py`. The task is implemented using the `BashOperator` class from the `airflow.operators.bash_operator` module.

The DAG is defined using the `DAG` class from the `airflow` module. The `default_args` dictionary contains some default arguments that will be used by all tasks in the DAG, unless they are overridden. The most important arguments are:

-   `owner`: The owner of the DAG. This is a required argument.
-   `depends_on_past`: Whether the task depends on the success of the previous run. This is set to `False`.
-   `start_date`: The start date of the DAG. This is set to March 6th, 2023.
-   `retries`: The number of times to retry the task in case of failure. This is set to `1`.
-   `retry_delay`: The delay between retries. This is set to 5 minutes.

The `dag` object is passed as a parameter to the `BashOperator` constructor to assign the task to the DAG.


## Running the DAG

To run the DAG, save the code to a file (e.g. `backup_dag.py`) and put it in your Airflow DAGs folder. Then start the Airflow scheduler and webserver:

Copy code

`airflow scheduler
airflow webserver` 

You should now be able to see the DAG in the Airflow UI and trigger it manually or wait for the scheduled run.
</details>
