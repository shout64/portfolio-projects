# Class Data ETL Scripts
 A Python script with SQL queries I wrote to pull data from an SIS (student information system), and load it into a course survey system.
 
**queries.py** is a python script with multiple queries to run against the SIS. These are utilized in <u>main.py</u> for gathering data.

**main.py** is a script that has a dictionary with each query from <u>queries.py</u>. This dictionary also contains the filename for each CSV that is generated with each query. The script connects to the SIS database, then loops through the dictionary and runs each query and generates a new CSV file with the appropriate file name. Then it connects to the survey system's SFTP folder and copies each file into the directory.
