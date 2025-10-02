from   datetime import date, datetime, timedelta
from   dotenv   import load_dotenv
import paramiko
import pyodbc
import csv
import os

load_dotenv()
username    = os.environ.get("db_user")
password    = os.environ.get("db_pass") 
server      = os.environ.get("server")
database    = os.environ.get("database")
sftp_user   = os.environ.get("sftp_user")
sftp_key    = os.environ.get("sftp_key")
sftp_host   = os.environ.get("sftp_host")
sftp_port   = os.environ.get("sftp_port")

days_to_keep = timedelta(days=5)
today_str    = date.today().strftime("%Y%m%d")
today_date   = date.today()
file_name    = f"data_{today_str}.csv"
local_folder = "C:\\Scripts\\data\\"
local_path   = local_folder + file_name
remote_path  = f"//data//{file_name}"

print("Connecting to database...")

cnxn   = pyodbc.connect("DRIVER={ODBC Driver 18 for SQL Server};SERVER=" + server + ";DATABASE=" + database + ";ENCRYPT=yes;UID=" + username + ";PWD=" + password + ";TrustServerCertificate=yes;")
cursor = cnxn.cursor()

print("Running query...")

cursor.execute("{Call SP_FINANCIAL_STUDENT_CHARGES_REPORT}")
results = cursor.fetchall()
cnxn.commit()

columns_list = [column[0] for column in cursor.description]
columns      = ", ".join(columns_list)
cnxn.close()

print("Generating CSV...")

with open(local_path, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(columns_list)
    writer.writerows(results)

print("Connecting to SFTP...")

try:
    private_key = paramiko.Ed25519Key.from_private_key_file(sftp_key, password=None)
    ssh_client  = paramiko.SSHClient()

    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=sftp_host, port=sftp_port, username=sftp_user, pkey=private_key)

    print("Copying file...")
    with ssh_client.open_sftp() as sftp:
        sftp.put(localpath=local_path, remotepath=remote_path)
        
    print("SFTP Transfer complete!")
        
except paramiko.AuthenticationException:
    print("Authentication failed. Please check username or private key.")
except paramiko.SSHException as e:
    print(f"SSH Error: {e}")
except FileNotFoundError:
    print(f"Local file not found: {local_path}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    ssh_client.close()

data = os.listdir(local_folder)

for file in data:
    file_date       = datetime.strptime(file[-12:-4], "%Y%m%d").date()
    date_to_compare = today_date - days_to_keep
    
    if file_date < date_to_compare:
        os.remove(local_folder + file)
        
print(f"\nRemoved files older than: {date_to_compare}")
