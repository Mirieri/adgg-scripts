import mysql.connector
import pandas as pd
from collections import defaultdict

# Initialize empty dictionaries for counting children of each father and mother
father_children_count = defaultdict(int)
mother_children_count = defaultdict(int)

# Connect to MySQL database
try:
    cnx = mysql.connector.connect(user='root', password='', host='localhost', database='adgg', auth_plugin='mysql_native_password')
except mysql.connector.Error as err:
    print(f"Error: {err}")
    exit(1)

cursor = cnx.cursor()

# Execute SQL query safely to retrieve information for all animals with a sire and dam
query = "SELECT id AS animal_id, tag_id AS animal_tag_id, sire_id AS father_id, sire_tag_id AS father_tag_id, dam_id AS mother_id, dam_tag_id AS mother_tag_id FROM core_animal WHERE sire_id IS NOT NULL AND dam_id IS NOT NULL"
cursor.execute(query)

# Loop through result set and count number of children for each father and mother
for (_, _, father_id, _, mother_id, _) in cursor:
    father_children_count[father_id] += 1
    mother_children_count[mother_id] += 1

# Find father ID with most number of children and mother ID with most number of children
most_children_father = max(father_children_count, key=father_children_count.get)
most_children_mother = max(mother_children_count, key=mother_children_count.get)

# Execute SQL parameterized query to retrieve information for chosen father and mother
father_query = "SELECT id AS animal_id, tag_id AS animal_tag_id, sire_id AS father_id, \
                sire_tag_id AS father_tag_id, dam_id AS mother_id, dam_tag_id AS mother_tag_id \
                FROM core_animal WHERE sire_id = %s and core_animal.country_id = 12"
mother_query = "SELECT id AS animal_id, tag_id AS animal_tag_id, sire_id AS father_id, \
                sire_tag_id AS father_tag_id, dam_id AS mother_id, dam_tag_id AS mother_tag_id \
                FROM core_animal WHERE dam_id = %s and core_animal.country_id = 12"
bisexual_query = "SELECT DISTINCT father.id AS animal_id, father.tag_id AS animal_tag_id, \
                father.sire_id AS father_id, father.sire_tag_id AS father_tag_id, mf.dam_id AS mother_id,\
                mf.dam_tag_id AS mother_tag_id FROM core_animal AS father \
                JOIN core_animal AS mf ON father.dam_id = mf.sire_id and father.sire_id = mf.sire_id \
                where father.country_id = 12"
dam_tag_missing_query = "SELECT id AS animal_id, tag_id AS animal_tag_id, sire_id AS father_id, \
                sire_tag_id AS father_tag_id, dam_id AS mother_id, dam_tag_id AS mother_tag_id \
                FROM core_animal WHERE dam_tag_id != '' AND dam_id IS NOT NULL AND \
                 core_animal.country_id = 12 AND dam_tag_id NOT IN (SELECT tag_id FROM core_animal)"
duplicates_query = "SELECT id as animal_id, tag_id as animal_tag_id, COUNT(*) as num_duplicates \
                    FROM core_animal GROUP BY id, animal_tag_id HAVING COUNT(*) > 1 "
sire_tag_missing_query = "SELECT id AS animal_id, tag_id AS animal_tag_id, sire_id AS father_id, \
                sire_tag_id AS father_tag_id, dam_id AS mother_id, dam_tag_id AS mother_tag_id \
                FROM core_animal WHERE sire_tag_id != '' AND dam_id IS NOT NULL \
                AND  core_animal.country_id = 12 AND sire_tag_id NOT IN (SELECT tag_id FROM core_animal)"

cursor.execute(father_query, (most_children_father,))
father_results = cursor.fetchall()
df_father = pd.DataFrame(father_results,
                         columns=['animal_id', 'animal_tag_id', 'sire_id', 'sire_tag_id', 'dam_id',
                                  'dam_tag_id'])

cursor.execute(mother_query, (most_children_mother,))
mother_results = cursor.fetchall()
df_mother = pd.DataFrame(mother_results,
                         columns=['animal_id', 'animal_tag_id', 'sire_id', 'dam_tag_id', 'dam_id',
                                  'dam_tag_id'])

cursor.execute(bisexual_query)
bisexual_results = cursor.fetchall()
df_bisexual = pd.DataFrame(bisexual_results,
                           columns=['animal_id', 'animal_tag_id', 'sire_id', 'sire_tag_id', 'dam_id',
                                    'dam_tag_id'])

cursor.execute(dam_tag_missing_query)
missing_dam_results = cursor.fetchall()
df_missing_dam = pd.DataFrame(missing_dam_results,
                              columns=['animal_id', 'animal_tag_id', 'sire_id', 'sire_tag_id', 'dam_id',
                                       'dam_tag_id', ])

cursor.execute(sire_tag_missing_query)
sire_tag_missing_results = cursor.fetchall()
df_sire_tag_missing_mismatch = pd.DataFrame(sire_tag_missing_results,
                                            columns=['animal_id', 'animal_tag_id', 'sire_id', 'sire_tag_id',
                                                     'dam_id', 'dam_tag_id', ])

cursor.execute(duplicates_query)
duplicates_data = cursor.fetchall()
df_duplicates = pd.DataFrame(duplicates_data, columns=['animal_id', 'animal_tag_id', 'num_duplicates'])


# Write results to Excel file on separate sheets
with pd.ExcelWriter('Pedigree Report.xlsx') as writer:
    df_father.to_excel(writer, sheet_name='SireWithMostAnimalSired', index=False)
    df_mother.to_excel(writer, sheet_name='DamWithMostCalves', index=False)
    df_bisexual.to_excel(writer, sheet_name='Bisexual Parents', index=False)
    df_missing_dam.to_excel(writer, sheet_name='Dam Tag ID Mismatches', index=False)
    df_sire_tag_missing_mismatch.to_excel(writer, sheet_name='Sire Tag ID Mismatches', index=False)
    df_duplicates.to_excel(writer, sheet_name='Duplicate Animal Tag IDs', index=False)

# Close database connection and cursor
cursor.close()
cnx.close()
