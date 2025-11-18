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
today_date   = date.today()
today_str    = today_date.strftime("%Y%m%d")
local_folder = "C:\\Scripts\\data\\"

def get_db_connection():
    cnxn   = pyodbc.connect("DRIVER={ODBC Driver 18 for SQL Server};SERVER=" + server + ";DATABASE=" + database + ";ENCRYPT=yes;UID=" + username + ";PWD=" + password + ";TrustServerCertificate=yes;")
    cursor = cnxn.cursor()
    return cnxn, cursor

def get_new_filename(prefix):
    return f"{prefix}_{today_str}.csv"

def run_stored_procedure(sp_name):
    print(f"Connecting to database...\nRunning {sp_name}")
    cnxn, cursor = get_db_connection()
    command = "{Call " + sp_name + "}"
    cursor.execute(command)
    results = cursor.fetchall()
    cnxn.commit()

    columns_list = [column[0] for column in cursor.description]

    return columns_list, results

def create_csv(columns, data, filename):
    local_path = local_folder + filename

    print(f"Generating {filename}...")

    with open(local_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        writer.writerows(data)

def send_files_to_finance(files_to_send: list):
    try:
        private_key = paramiko.Ed25519Key.from_private_key_file(sftp_key, password=None)
        ssh_client  = paramiko.SSHClient()

        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=sftp_host, port=sftp_port, username=sftp_user, pkey=private_key)

        with ssh_client.open_sftp() as sftp:
            for file in files_to_send:
                local_path  = local_folder + file
                remote_path = f"//data//{file}"
                print(f"Copying {file}...")
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

def remove_old_files():
    data = os.listdir(local_folder)

    for file in data:
        file_date       = datetime.strptime(file[-12:-4], "%Y%m%d").date()
        date_to_compare = today_date - days_to_keep
        
        if file_date < date_to_compare:
            os.remove(local_folder + file)
        
    print(f"\nRemoved files older than: {date_to_compare}")

def main():
    # Student Data
    student_file = get_new_filename("STUDENT")
    stud_columns, stud_data = run_stored_procedure("SP_FINANCIAL_STUDENT_CHARGES_REPORT")
    create_csv(stud_columns, stud_data, student_file)

    # Non-Student Data
    non_student_file = get_new_filename("NON_STUDENT")
    non_stud_columns, non_stud_data = run_stored_procedure("SP_NON_STUDEND_CHARGES_REPORT")
    create_csv(non_stud_columns, non_stud_data, non_student_file)

    files_to_send = [student_file, non_student_file]
    send_files_to_finance(files_to_send)
    remove_old_files()

if __name__ == "__main__":
    main()
