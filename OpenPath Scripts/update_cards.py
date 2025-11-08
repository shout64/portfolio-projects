# Example script for large batch updating user badge info in Alta Open (formerly OpenPath)
# Some details changed for anonymity
from dotenv import load_dotenv
import os
import requests
import pandas as p

load_dotenv()
payload = os.getenv("PAYLOAD")

LoginUrl = "https://api.openpath.com/auth/login"
LoginHeaders = {
    "accept": "application/json",
    "content-type": "application/json"
}

#Login to OpenPath
response = requests.post(LoginUrl, json=payload, headers=LoginHeaders)

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
    # Gets all users with Student Emails and status:(A)
    url = f"{base_url}/users?limit=1000&offset={offset}&sort=identity.lastName&order=asc&filter=status%3A%28A%29%20identity.email%3A%28%40studentemail.com%29&withBuildings=false&isAttachedToAtLeastOneIntercom=false"
    
    data = requests.get(url, headers=headers)
    json_data = data.json()
    for i in range(len(json_data['data'])):
        user_id = json_data['data'][i]['id']
        raw_email = json_data['data'][i]['identity']['email']
        user_email = raw_email.lower()

    # Store results in a all_responses list
        all_responses.append(
            {
                "user": user_id,
                "email": user_email
             }
        )
    # If there are more results, offest the call by 1000 and get more users. End loop if there are no more results
    if len(json_data['data']) < 1000:
        has_more_results = False
    else:
        offset += 1000

# Setup dataframes for the data and match them together
op_data = p.DataFrame(all_responses)
cards = p.read_csv("OpenPathExport.csv")
matching_rows = cards.merge(op_data,on=["email"], how="inner")

# Loop through all users and add their card number
for i in range(len(matching_rows)):
    url = f"https://api.openpath.com/orgs/ORG-ID/users/{matching_rows.iloc[i]['user']}/credentials"

    user_card = str(matching_rows.iloc[i]["Card ID"])

    payload = {
        "card": {
            "fields": {
                "cardId": user_card,
                "facilityCode": "233"
            },
            "cardFormatId": 5150,
            "isOutputEnabled": True
        },
        "credentialTypeId": 2
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": jwt_token
    }
    card_response = requests.post(url, json=payload, headers=headers)
    json_card_response = card_response.json()
    if  card_response.status_code == 201:
        print(f"Card added successfully for {matching_rows.iloc[i]["email"]}. Status code: {card_response.status_code}")
    elif card_response.status_code == 400:
        print(f"Card is duplicate for {matching_rows.iloc[i]["email"]}. Status code: {card_response.status_code}")
    else:
        print(f"----\nERROR: Card for {matching_rows.iloc[i]["email"]} was not added.\nStatus code: {card_response.status_code}\n----")

#Logout of OpenPath
logout_url = "https://api.openpath.com/auth/logout"
headers = {"Authorization": jwt_token}
logout_response = requests.post(logout_url, headers=headers)
