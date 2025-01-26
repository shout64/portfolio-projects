# Example script for deleting a large batch of user cards from Alta Open (formerly OpenPath)
# Some details changed for anonymity

import requests
import creds as c

LoginUrl = "https://api.openpath.com/auth/login"
LoginHeaders = {
    "accept": "application/json",
    "content-type": "application/json"
}

#Login to OpenPath
response = requests.post(LoginUrl, json=c.temp_payload, headers=LoginHeaders)

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

    #Gets all credentials with student email addresses
    url = f"{base_url}/credentials?limit=1000&offset={offset}&sort=id&order=asc&filter=identity.email%3A%28%40studentemail.com%29"
    
    data = requests.get(url, headers=headers)
    json_data = data.json()
    for i in range(len(json_data['data'])):
        credential_id = json_data['data'][i]['id']
        user_id = json_data['data'][i]['user']['id']
        user_email = json_data['data'][i]['user']['identity']['email']

    # Store results in all_reponses list
        all_responses.append(
            {
                "credential": credential_id,
                "user": user_id,
                "email": user_email
             }
        )
    # If there are more results, offest the call by 1000 and get more users. End loop if there are no more results
    if len(json_data['data']) < 1000:
        has_more_results = False
    else:
        offset += 1000

#Loop through all users and delete their credentials
for i in range(len(all_responses)):
    try:
        url = f"https://api.openpath.com/orgs/43948/users/{all_responses[i]["user"]}/credentials/{all_responses[i]["credential"]}"
        headers = {"Authorization": jwt_token}
        response = requests.delete(url, headers=headers)

        print(f"Credential for {all_responses[i]["email"]} was deleted.")
    except:
        print(f"Error with user {all_responses[i]["user"]}")
        print(response.text)


#Logout of OpenPath
logout_url = "https://api.openpath.com/auth/logout"
headers = {"Authorization": jwt_token}
logout_response = requests.post(logout_url, headers=headers)
