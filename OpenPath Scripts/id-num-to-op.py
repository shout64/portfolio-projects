# Example script for updating user info in Alta Open (formerly OpenPath) from local ERP
# Some details changed for anonymity

import requests
import logging as log
import pyodbc
import creds as c

# Re-write a log file every time this script runs
log.basicConfig(filename='id-num-to-op.log', level=log.WARNING)
try:
    with open('prox-to-ad.log', 'w'):
        pass
except:
    print("No log file present, a new one will be created.")

LoginUrl = "https://api.openpath.com/auth/login"
LoginHeaders = {
    "accept": "application/json",
    "content-type": "application/json"
}

#Login to OpenPath
response = requests.post(LoginUrl, json=c.payload, headers=LoginHeaders)

#Get JWT Token for remaining API calls
if response.status_code == 201:
    json_response = response.json()
    jwt_token = json_response["data"]["token"]
    print(f"OpenPath Login successful. Status code : {response.status_code}")
else:
    print(f"Failure to authenticate. Status code: {response.status_code}")

# Set variables for getting user information
base_url = "https://api.openpath.com/orgs/ORG-ID"

headers = {
    "accept": "application/json",
    "Authorization": jwt_token
}

all_responses = []
offset = 0
has_more_results = True

while has_more_results == True:
    current_user_index = 0

    # Gets all Users with no External ID in batches of 1000.
    url = f"{base_url}/users?limit=1000&offset={offset}&sort=id&order=asc&filter=externalId%3A%28null%29status%3A%28A%29%20"

    data = requests.get(url, headers=headers)
    json_data = data.json()
    for i in range(len(json_data['data'])):
        user_email = json_data['data'][i]['identity']['email']
        user_externalID = json_data['data'][i]['externalId']
        user_title = json_data['data'][i]['title']        
        user_op_id = json_data['data'][i]['id']

    # Store results in all_reponses list
        all_responses.append(
            {
                "email": user_email,
                "externalID": user_externalID,
                "title": user_title,
                "op_id": user_op_id
             }
        )
    # If there are more results, offest the call by 1000 and get more users. End loop if there are no more results
    if len(json_data['data']) < 1000:
        has_more_results = False
    else:
        offset += 1000

#Create string of users who need ID NUMs
#If user has a quotation mark in their name, add a second quote to escape it for the SQL query
users_needing_updates = ""
for user in all_responses:
    single_quote_index = user["email"].find("'")
    if single_quote_index == -1:
        users_needing_updates += "'" + user["email"] + "', "
    else:
        users_needing_updates += "'" + user["email"][:single_quote_index] + "'" + user["email"][single_quote_index:] + "', "

#Remove final comma and space
users_needing_updates = users_needing_updates[:-2]

# Connect to database
server = 'DATABASE SERVER'
database = 'DB NAME'
cnxn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};''SERVER='+server+';DATABASE='+database+';ENCRYPT=yes;UID='+c.db_username+';PWD='+c.db_password+';TrustServerCertificate=yes;')
cursor = cnxn.cursor()

#Fetch new info and update all_responses. Use lower() to catch all accounts that need updating.
for row in cursor.execute(f"""
            SElECT nm.EMAIL_ADDRESS, nm.ID_NUM as 'externalID', nm.TITLE
            FROM NAME_MASTER nm
            WHERE nm.EMAIL_ADDRESS in ({users_needing_updates});"""):
    for i in range(len(all_responses)):
        if all_responses[i]["email"].lower() == row.EMAIL_ADDRESS.lower():
            all_responses[i]["externalID"] = str(row.externalID)
            all_responses[i]["title"] = row.TITLE

# Loop through each member of all_responses and if 
# they have a Jenzabar ID then run API call to update user information.
user_accounts_updated = 0

for i in range(len(all_responses)):
    if all_responses[i]["externalID"] != None:
        # Updating J1 ID and Title
        update_url = f"{base_url}/users/{all_responses[i]["op_id"]}"

        update_payload = {
            "externalId": all_responses[i]["externalID"],
            "title": all_responses[i]["title"]

        }
        update_headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": jwt_token
        }

        update_response = requests.patch(update_url, json=update_payload, headers=update_headers)

        if update_response.status_code == 200:
            print(f"User ID and Title updated: {all_responses[i]["email"]}")
        else:
            print(f"""FAILED TO UPDATE ID NUMBER AND TITLE\nUser: {all_responses[i]["email"]}\nOP ID: {all_responses[i]["op_id"]}\n
                  Status code: {update_response.status_code}\nUpdate Response: {update_response.json()}\n""")
            
        # Updating University Library ID
        opid = all_responses[i]['op_id']
        url = f"https://api.openpath.com/orgs/ORG-ID/users/{opid}/customFields/6307"

        payload = { "value": "LIBRARY ID" }

        response = requests.patch(url, json=payload, headers=headers)

        print(response.text)

        if response.status_code == 204:
            print(f"University Library ID updated: {all_responses[i]["email"]}.")
            user_accounts_updated += 1
        else:
            print(f"""FAILED TO UPDATE UNIVERSITY LIBRARY ID\nUser: {all_responses[i]["email"]}\nOP ID: {opid}\n
                    Status code: {response.status_code}\nUpdate Response: {response.json()}\n""")
    else:
        print(f"No Jenzabar ID match for {all_responses[i]["email"]}.")

print(f"IDs and Titles Updated: {user_accounts_updated}")


#Logout of OpenPath
logout_url = "https://api.openpath.com/auth/logout"
headers = {"Authorization": jwt_token}
logout_response = requests.post(logout_url, headers=headers)
