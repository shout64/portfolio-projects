from dotenv import load_dotenv
import queries as q
import paramiko
import pyodbc
import os
import csv

load_dotenv()
username      = os.environ.get("db_user")
password      = os.environ.get("db_pass") 
server        = os.environ.get("server")
database      = os.environ.get("database")
sftp_user     = os.environ.get("sftp_user")
sftp_key      = os.environ.get("sftp_key")
sftp_host     = os.environ.get("sftp_host")
sftp_port     = os.environ.get("sftp_port")

local_folder  = "C:\\scripts\\data\\"
remote_folder = f"//test//school//upload//"

query_tasks = [
    {
        "query": q.students,
        "filename": "students.csv",
     },
     {
         "query": q.faculty_and_staff,
         "filename": "faculty-and-staff.csv",
     },
     {
         "query": q.courses,
         "filename": "courses.csv",
     },
     {
         "query": q.terms,
         "filename": "terms.csv",
     },
     {
         "query": q.course_sections,
         "filename": "course-sections.csv",
     },
     {
         "query": q.student_enrollments,
         "filename": "student-enrollments.csv",
     },
     {
         "query": q.instructor_assignments,
         "filename": "instructor-assignments.csv",
     },
]

print("Connecting to database...")

cnxn   = pyodbc.connect("DRIVER={ODBC Driver 18 for SQL Server};SERVER=" + server + ";DATABASE=" + database + ";ENCRYPT=yes;UID=" + username + ";PWD=" + password + ";TrustServerCertificate=yes;")
cursor = cnxn.cursor()

for query in query_tasks:
    cursor.execute(query["query"])
    results = cursor.fetchall()

    columns_list = [column[0] for column in cursor.description]
    columns      = ", ".join(columns_list)
    new_file     = local_folder + query["filename"]
    
    print(f"Generating {query['filename']}...")

    with open(new_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(columns_list)
        writer.writerows(results)

cnxn.close()

print("Connecting to SFTP...")

try:
    private_key = paramiko.Ed25519Key.from_private_key_file(sftp_key, password=None)
    ssh_client  = paramiko.SSHClient()

    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=sftp_host, port=sftp_port, username=sftp_user, pkey=private_key)

    data = os.listdir(local_folder)
    for file in data:
        local_path  = local_folder + file
        remote_path = remote_folder + file
        print(f"Copying {file}...")
        
        with ssh_client.open_sftp() as sftp:
            sftp.put(localpath=local_path, remotepath=remote_path)
        
    print("SFTP Transfer complete!")
        
except paramiko.AuthenticationException:
    print("Authentication failed. Please check your username, password, or private key.")
except paramiko.SSHException as e:
    print(f"SSH Error: {e}")
except FileNotFoundError:
    print(f"Local file not found: {local_path}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    ssh_client.close()
