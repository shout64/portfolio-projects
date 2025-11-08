# Example script for user badge info in local ERP and AD from Alta Open (formerly OpenPath)
# Some details changed for anonymity

from ms_active_directory import ADDomain
from dotenv import load_dotenv
import os
import requests
import logging as log
import pyodbc

load_dotenv()
payload = os.getenv("PAYLOAD")
ad_user = os.getenv("AD_USER")
ad_pass = os.getenv("AD_PASSWORD")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")

# Re-write a log file every time this script runs
log.basicConfig(filename='prox-to-ad.log', level=log.WARNING)
try:
    with open('prox-to-ad.log', 'w'):
        pass
except:
    print("No log file present, a new one will be created.")

LoginUrl     = "https://api.openpath.com/auth/login"
LoginHeaders = {
    "accept": "application/json",
    "content-type": "application/json"
}

#Login to OpenPath
response = requests.post(LoginUrl, json=payload, headers=LoginHeaders)

#Get JWT Token for remaining API calls
if response.status_code == 201:
    json_response = response.json()
    jwt_token     = json_response["data"]["token"]
    print(f"OpenPath Login successful. Status code : {response.status_code}")
else:
    print(f"Failure to authenticate. Status code: {response.status_code}")

# Set variables for getting user information
base_url = "https://api.openpath.com/orgs/ORG-ID"

headers = {
    "accept"        : "application/json",
    "Authorization" : jwt_token
}

all_responses    = []
offset           = 0
has_more_results = True

while has_more_results == True:
    current_user_index = 0

    #Gets all credentials with Facility Code ###
    url = f"{base_url}/credentials?limit=1000&offset={offset}&sort=id&order=asc&filter=card.facilityCode%3A%28FACILITY-CODE%29"

    data = requests.get(url, headers=headers)
    json_data = data.json()
    for i in range(len(json_data['data'])):
        user_email  = json_data['data'][i]['user']['identity']['email']
        user_card   = json_data['data'][i]['card']['cardId']
        user_id_num = json_data['data'][i]['user']['externalId']

    # Store results in all_reponses list
        all_responses.append(
            {
                "email"   : user_email,
                "PROX_ID" : user_card,
                "ID_NUM"  : user_id_num
             }
        )
    # If there are more results, offest the call by 1000 and get more users. End loop if there are no more results
    if len(json_data['data']) < 1000:
        has_more_results = False
    else:
        offset += 1000

# Logout of OpenPath
logout_url      = "https://api.openpath.com/auth/logout"
headers         = {"Authorization": jwt_token}
logout_response = requests.post(logout_url, headers=headers)

# Connect to AD
domain = ADDomain('DOMAIN ADDRESS')
session = domain.create_session_as_user(ad_user, ad_pass)

def prox_to_pager(email, prox):
    # Get user by email address. Returns list
    user = session.find_users_by_attribute(attribute_name="mail", attribute_value=email, size_limit=1)

    # Overwrite pager with PROX_ID. Get first item in list
    update = session.overwrite_attribute_for_user(user[0].get('sAMAccountName'), 'pager', prox)

# Update each user's Pager field in AD
for i in range(len(all_responses)):
    try:
        prox_to_pager(email=all_responses[i]['email'], prox=all_responses[i]['PROX_ID'])
        print(f"User {all_responses[i]['email']} successfully updated!")
    except:
        print(f"User with email {all_responses[i]['email']} was not updated. ERROR")
        log.warning(all_responses[i]['email'] + "could not be updated.")

print(f"Number of attempted updates: {len(all_responses)}")

# Connect to database
server   = 'SERVER NAME'
database = 'DB NAME'
cnxn     = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};''SERVER='+server+';DATABASE='+database+';ENCRYPT=yes;UID='+db_user+';PWD='+db_pass+';TrustServerCertificate=yes;')
cursor   = cnxn.cursor()

# Update PROX ID in NAME_MASTER_UDF
for i in range(len(all_responses)):
    if all_responses[i]['ID_NUM'] != None and all_responses[i]['ID_NUM'] != '':
        prox_num = all_responses[i]['PROX_ID']
        id_num   = all_responses[i]['ID_NUM']
        cursor.execute(f"""
                        UPDATE NAME_MASTER_UDF
                        SET PROX_ID = {prox_num}
                        WHERE ID_NUM = {id_num};""")
        cnxn.commit()
        print(f"NAME_MASTER_UDF - PROX_ID has been updated for {all_responses[i]['ID_NUM']}")
    else:
        print(f"No ID Number for user {all_responses[i]['email']}")
