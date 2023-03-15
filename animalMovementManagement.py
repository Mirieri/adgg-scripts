import mysql.connector
from dotenv import load_dotenv
import os
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime

# Load the .env file
load_dotenv()


def connect_to_db():
    # Connect to the database using mysql credentials from .env file
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    return conn


# Function to send email with CSV attachment and report
def send_email_with_report():
    # Connect to the database
    conn = connect_to_db()
    cur = conn.cursor()

    # Execute the SQL query
    query = """
         SELECT
                  core_animal_event.animal_id,
                  core_animal.tag_id,
                  previous_farmer.name as previous_farmer,
                  previous_farmer.id as previous_farmer_id,
                  current_farmer.name as new_farmer,
                  current_farmer.id as current_farmer_id,
                  region.name as region,
                  district.name as district,
                  ward.name as ward,
                  village.name as village
        FROM
            core_animal
        INNER JOIN core_animal_event ON core_animal.id = core_animal_event.animal_id
        INNER JOIN core_farm  current_farmer ON REPLACE(IFNULL(JSON_EXTRACT(core_animal_event.additional_attributes, '$."557"'), ''), '"', '') = current_farmer.id
        INNER JOIN core_farm as previous_farmer on core_animal.farm_id  = previous_farmer.id
        INNER JOIN country_units region ON current_farmer.region_id = region.id
        INNER JOIN country_units district ON current_farmer.district_id = district.id
        INNER JOIN country_units ward ON current_farmer.ward_id = ward.id
        INNER JOIN country_units village ON current_farmer.village_id = village.id
        WHERE event_type = 9 order by core_animal.country_id asc;
    """

    try:
        cur.execute(query)
        # Export data as CSV
        columns = ['Animal ID', 'Current Farm ID', 'New Farm ID', 'Region ID', 'District ID', 'Ward ID', 'Village ID']
        data = cur.fetchall()
        csv_content = [columns]
        for row in data:
            csv_content.append(row)

        csv_filepath = 'updated_records.csv'
        with open(csv_filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            for line in csv_content:
                writer.writerow(line)

        # Send email with CSV attachment
        msg = MIMEMultipart()
        msg['From'] = 'noreply.adgg@gmail.com'  # Replace with your own email address
        recipients = ['d.mogaka@cgiar.org', 'a.hassen@cgiar.org', 'g.kipkosgei@cgiar.org', 'neemajkelya@gmail.com', 'j.ojango@cgiar.org','r.mrode@cgiar.org']
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = 'Update to show Movement of Animals to new Farms'

        # Create report text
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        body = f"****** This is a system generated report ******\n\nReporting Date: {now}\n\nPlease find attached CSV showing animal movement this week.\n\nBest Regards,\nDavid"

        msg.attach(MIMEText(body, 'plain'))

        with open(csv_filepath, "rb") as fh:
            attach = MIMEApplication(fh.read(), _subtype="csv")
            attach.add_header('Content-Disposition', 'attachment', filename=str(csv_filepath))
            msg.attach(attach)

        smtp = smtplib.SMTP('smtp.gmail.com', 587)  # Replace with your SMTP server and port details
        smtp.starttls()
        smtp.login('noreply.adgg@gmail.com', 'rvpizpgabllbuwfo')  # Replace with your own email credentials
        smtp.sendmail(msg['From'], msg['To'], msg.as_string())
        smtp.quit()

    except Exception as e:
        print(f"Error executing query or sending email: {e}")

    finally:
        cur.close()
        conn.close()


# Function to execute the update query
def execute_update_query():
    # Connect to the database
    conn = connect_to_db()
    cur = conn.cursor()

    # Execute the SQL query
    query = """
        UPDATE
          core_animal
        INNER JOIN core_animal_event ON core_animal.id = core_animal_event.animal_id
        INNER JOIN core_farm ON REPLACE(IFNULL(JSON_EXTRACT(core_animal_event.additional_attributes, '$."557"'), ''), '"', '') = core_farm.id
        SET
          core_animal.farm_id = REPLACE(IFNULL(JSON_EXTRACT(core_animal_event.additional_attributes, '$."557"'), ''), '"', ''),
          core_animal.region_id = core_farm.region_id,
          core_animal.district_id = core_farm.district_id,
          core_animal.ward_id = core_farm.ward_id,
          core_animal.village_id = core_farm.village_id,
          core_animal.updated_at = NOW()
        WHERE
          event_type = 9;
    """

    try:
        cur.execute(query)
        conn.commit()
    except Exception as e:
        print(f"Error executing query: {e}")
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    send_email_with_report()
    execute_update_query()
