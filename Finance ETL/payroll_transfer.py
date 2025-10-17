from datetime import date, datetime, timedelta
from dotenv   import load_dotenv
import pandas as pd
import paramiko
import os

load_dotenv()

pay_hostname   = os.environ.get("pay_hostname")
pay_sftp_user  = os.environ.get("pay_sftp_user")
pay_sftp_pass  = os.environ.get("pay_sftp_pass")
sftp_user      = os.environ.get("sftp_user")
sftp_key       = os.environ.get("sftp_key")
sftp_host      = os.environ.get("sftp_host")
sftp_port      = os.environ.get("sftp_port")

csv_filename   = f"Payroll_{date.today().strftime("%Y%m%d")}.csv"
sftp_path      = "C:\\SFTP\\payroll\\"
local_path     = "C:\\Scripts\\payroll\\data\\"
local_hist     = "C:\\Scripts\\payroll\\hist\\"

def remove_old_files(folder):    
    days_to_keep    = timedelta(days=60) # Reports are ran every 2ish weeks, 60 days makes 4ish weeks worth of files
    data            = os.listdir(folder)
    today_date      = date.today()
    date_to_compare = today_date - days_to_keep
    removed_files   = []
    for file in data:
        try:
            file_date = datetime.strptime(file[-12:-4], "%Y%m%d").date()
        except ValueError:
            print(f"Not removing {file} from hist, date not found or date is in incorrect format.")
            continue
        
        if file_date < date_to_compare:
            removed_files.append(file)
            os.remove(folder + file)
    
    if len(removed_files) > 0:
        print(f"Removed files older than: {date_to_compare}\nFiles removed: {removed_files}")

#Pull Payroll files from SFTP
print("Connecting to Payroll SFTP...")
try:
    ssh_client = paramiko.SSHClient()

    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=pay_hostname, port=22, username=pay_sftp_user, password=pay_sftp_pass)

    with ssh_client.open_sftp() as sftp:
        file_list = sftp.listdir(sftp_path)
        
        if len(file_list) == 0:
            ssh_client.close()
            print("No files to import.\nExiting script.")
            exit()
        
        print("Copying files to server...")
        
        for file in file_list:
            remote = sftp_path + file
            local  = local_path + file
            sftp.get(remote, local)
            sftp.remove(remote)
            
except paramiko.AuthenticationException:
    print("Authentication failed with Payroll SFTP. Please check your username, password, or private key.")
except paramiko.SSHException as e:
    print(f"Payroll SSH Error: {e}")
except FileNotFoundError:
    print(f"Remote Payroll file not found: {remote}")
except Exception as e:
    print(f"An unexpected Payroll error occurred: {e}")
finally:
    ssh_client.close()
   
# Combine CSVs to one file
print("Consolidating files...")
all_dataframes = []

try:
    for file in os.listdir(local_path):
        filepath = os.path.join(local_path, file)
        all_dataframes.append(pd.read_csv(filepath))
    
    new_data = pd.concat(all_dataframes, ignore_index=True)
    new_data.to_csv(os.path.join(local_path, csv_filename), index=False)
except Exception as e:
    print(f"CSV Error: {e}")

print("Connecting to Finance SFTP...")
try:
    private_key   = paramiko.Ed25519Key.from_private_key_file(sftp_key, password=None)
    fn_ssh_client = paramiko.SSHClient()

    fn_ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    fn_ssh_client.connect(hostname=sftp_host, port=sftp_port, username=sftp_user, pkey=private_key)
    
    file_list   = os.listdir(local_path)
    remote_path = f"//Payroll//"
    
    print("Copying files to Finance SFTP...")
    
    with fn_ssh_client.open_sftp() as sftp:
        local  = os.path.join(local_path, csv_filename)
        remote = os.path.join(remote_path, csv_filename)
        sftp.put(local, remote)
            
# Move files to payroll\hist, rename if needed, and remove old files
        for file in file_list:
            local  = os.path.join(local_path, file)
            if file[-12:-4] != date.today().strftime("%Y%m%d"):
                file = file[:-4] + "_" + date.today().strftime("%Y%m%d") + file[-4:]
            
            if not os.path.exists(local_hist + file):
                os.rename(local, local_hist + file)
            else:
                os.remove(local)
            
    remove_old_files(local_hist)
        
    print("SFTP Transfer Complete!")
            
except paramiko.AuthenticationException:
    print("Authentication failed with Finance SFTP. Please check your username, password, or private key.")
except paramiko.SSHException as e:
    print(f"Finance SSH Error: {e}")
except FileNotFoundError:
    print(f"Local Finance file not found: {local}")
except Exception as e:
    print(f"An unexpected Finance error occurred: {e}")
finally:
    fn_ssh_client.close()
    

