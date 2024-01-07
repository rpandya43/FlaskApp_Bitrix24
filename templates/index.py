from flask import Flask, request, jsonify
from urllib.parse import parse_qs
import requests
import json 
from time import sleep
import urllib.parse
import datetime



app = Flask(__name__)

@app.route('/trigger-script', methods=['POST'])
def trigger_script():
    try:
         # Retrieve the raw data from the request
        raw_content = request.get_data().decode('utf-8')

        print('running')

        # Parse the raw data based on Content-Type header
        if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
            parsed_data = parse_qs(raw_content)
        elif request.headers.get('Content-Type') == 'text/plain':
            parsed_data = json.loads(raw_content)
        else:
            return jsonify({"error": "Invalid Content-Type"}), 400

        if 'data[FIELDS][ID]' in parsed_data:
            field_value = parsed_data['data[FIELDS][ID]'][0]

            # Create a dictionary to store the extracted value
            extracted_data = {'ID': field_value}

            print()
            print()

            print("Step 1, Extracted ID :", extracted_data)

            # Trigger the webhook using the extracted ID value
            webhook_url = f"https://rtech.bitrix24.com/rest/1/n0nai3kd6jtjp6ak/crm.lead.get.json?ID={field_value}"
            response = requests.get(webhook_url)

            if response.status_code == 200:
                data = response.json()
                result = data.get('result', {})

                print("Webhook Response:", data)  # Debug: Print the entire response

                # Extract and store specific fields from the JSON response
                stored_data = {
                    'TITLE': result.get('TITLE', ''),
                    'COMPANY_ID': result.get('COMPANY_ID', ''),
                    'Sector': result.get('UF_CRM_1669462784678', []),
                    'Responsible_id': result.get('ASSIGNED_BY_ID', ''),
                }

                print(stored_data['Responsible_id'])

                # Send a GET request to retrieve user data based on Responsible_id
                user_url = f"https://rtech.bitrix24.com/rest/1/n0nai3kd6jtjp6ak/user.get.json?ID={stored_data['Responsible_id']}"
                user_response = requests.get(user_url)

                if user_response.status_code == 200:
                    user_data = user_response.json()
                    user_result = user_data.get('result', [{}])[0]

                    # Extract and store user name and last name
                    user_stored_data = {
                        'RP': user_result.get('NAME', ''),
                        'RP_LAST': user_result.get('LAST_NAME', '')
                    }

                    print('Step 2, User Data:', user_stored_data)

                    Full_Name = f"{user_result.get('NAME', '')} {user_result.get('LAST_NAME', '')}"


                else:
                    print("User Data Request Failed:", user_response.text)
                    return jsonify({"error": "User data request failed"}), 500

                

                print('Step 2, Second API: '+ str(stored_data))

                # Create a dictionary to use the Sector ID and find the clear text version
                SECTOR = {
                    58: 'RTech_CRM_EDU',
                    56: 'RTech_CRM_ENERGYONG',
                    60: 'RTech_CRM_HC',
                    62: 'RTech_CRM_I.T&A.V',
                }

                sector_value = result.get('UF_CRM_1669462784678', [])
                sector = SECTOR.get(sector_value[0], 'Unknown')

                #print("Stored Data:", stored_data)
                print('Step 3, The Sector is : ' + sector)

                 # Trigger the second webhook using the extracted COMPANY_ID value
                company_id = result.get('COMPANY_ID', '')
                if company_id:
                    company_webhook_url = f"https://rtech.bitrix24.com/rest/1/a1swos03sn86qbns/crm.company.get.json?ID={company_id}"
                    company_response = requests.get(company_webhook_url)

                    if company_response.status_code == 200:
                        company_data = company_response.json()
                        company_result = company_data.get('result', {})

                        # Extract and store specific fields from the company JSON response
                        company_stored_data = {
                            'TITLE': company_result.get('TITLE', ''),
                            # Add more fields if needed
                        }

                        cus = company_stored_data['TITLE']

                        # Azure AD Application credentials
                        client_id = '02b268b9-f118-4d7c-8a87-f56853add793'
                        client_secret = 'dbT8Q~DWc_fQK_NIv5A9asBEZGlHT1ht8..-hdqZ'
                        tenant_id = 'b51fd322-76d3-4fe0-9e0a-40984ac1dcfd'

                        # Microsoft Graph API endpoint
                        graph_api_url = 'https://graph.microsoft.com/v1.0/'

                        # Authenticate and get access token
                        token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
                        token_data = {
                            'grant_type': 'client_credentials',
                            'client_id': client_id,
                            'client_secret': client_secret,
                            'scope': 'https://graph.microsoft.com/.default'
                        }
                        token_response = requests.post(token_url, data=token_data)
                        access_token = token_response.json()['access_token']

                        # Create a folder
                        #parent_folder_id = 'tenantId=b51fd322%2D76d3%2D4fe0%2D9e0a%2D40984ac1dcfd&siteId=%7B1022faa5%2D9c96%2D4f23%2Dabac%2De9232a66ee71%7D&webId=%7B4faa3929%2D7cf4%2D4127%2Da134%2D20372e8ab340%7D&listId=dd07b67d%2Dcaa4%2D4d3c%2Db8e1%2D6cf084b65cc8&webUrl=https%3A%2F%2Frtechqatar%2Esharepoint%2Ecom&version=1'

                        Tittle_var={stored_data['TITLE']}

                        if "/" in Tittle_var:
                            # Replace "/" with "-"
                            Tittle_var = Tittle_var.replace("/", "-")

                        folder_name = f"{extracted_data['ID']}  {Tittle_var}"

                        drive_id_ong = 'b!dNYn6KfbD0Ws6l-EFMOeUsNV2mYfOYhCkouRqBMJlxowaZxCb2drQbyajIF6qw1x'
                        drive_id_hc = 'b!dNYn6KfbD0Ws6l-EFMOeUsNV2mYfOYhCkouRqBMJlxqnDxggUT1CRIsDy0Q3njyo'
                        drive_id_edu = 'b!dNYn6KfbD0Ws6l-EFMOeUsNV2mYfOYhCkouRqBMJlxouK5-XNLP7Sb-Y8EcTtaV_'
                        drive_id_it = 'b!dNYn6KfbD0Ws6l-EFMOeUsNV2mYfOYhCkouRqBMJlxq-VQoCk7fJR5cuA5Knkn75'

                        #cus = 'Pia'

                        today = datetime.date.today()
                        year = today.year

                        Folder_Location = f'root:/{year}/{cus}:'

                        if sector == 'RTech_CRM_ENERGYONG':
                            folder_endpoint = f'{graph_api_url}drives/{drive_id_ong}/items/{Folder_Location}/children'
                        else :
                            if sector == 'RTech_CRM_HC':
                                folder_endpoint = f'{graph_api_url}drives/{drive_id_hc}/items/{Folder_Location}/children'
                            else: 
                                if sector == 'RTech_CRM_EDU':
                                    folder_endpoint = f'{graph_api_url}drives/{drive_id_edu}/items/{Folder_Location}/children'
                                else:
                                    if sector == 'RTech_CRM_I.T&A.V':
                                        folder_endpoint = f'{graph_api_url}drives/{drive_id_it}/items/{Folder_Location}/children'
                                    else:
                                        print ("Sector DropDown Error")

                        dict2 = [
                                    "01 RFQ",
                                    "02 Vendor Quotes",
                                    "03 Costing",
                                    "04 Customer Quotes",
                                    "05 Deal Files"
                                ]
                        dict1 = ["01 Customer","02 Vendor"]
                        dict3 = ['02 bit']

                        
                        folder_data = {
                        'name': folder_name,
                        'folder': {},
                        '@microsoft.graph.conflictBehavior': 'rename'
                        }

                        headers = {
                            'Authorization': f'Bearer {access_token}',
                            'Content-Type': 'application/json'
                        }

                        response = requests.post(folder_endpoint, json=folder_data, headers=headers)

                        if response.status_code == 201:
                            print(f"Step 4, Folder '{folder_name}' created successfully in {cus}'s folder")
                            data = response.json()
                            folder_id = data.get('id', '')
                            access_link = data.get('webUrl', '')

                            print('!!! The Folders ID is '+ folder_id + '!!!')
                            print('*** To Access the Folder Please Click Here : '+ access_link + '***')
                            # webbrowser.open(access_link) # Un Hash to open URL in NON PROD development Area
                            # Reload the Folder Location and start from inside the newly created folder 
                            
                            Folder_Location=f'root:{year}/{cus}/{folder_name}:'

                            if sector == 'RTech_CRM_ENERGYONG':
                                folder_endpoint_2 = f'{graph_api_url}drives/{drive_id_ong}/items/{Folder_Location}/children'
                            else :
                                if sector == 'RTech_CRM_HC':
                                    folder_endpoint_2 = f'{graph_api_url}drives/{drive_id_hc}/items/{Folder_Location}/children'
                                else: 
                                    if sector == 'RTech_CRM_EDU':
                                        folder_endpoint_2 = f'{graph_api_url}drives/{drive_id_edu}/items/{Folder_Location}/children'
                                    else:
                                        if sector == 'RTech_CRM_I.T&A.V':
                                            folder_endpoint_2 = f'{graph_api_url}drives/{drive_id_it}/items/{Folder_Location}/children'
                                        else:
                                            print ("Sector DropDown Error")

                            print ( folder_endpoint )

                            for i in dict2:
                                print(str(Folder_Location))
                                fd = {
                                'name': i,
                                'folder': {},
                                '@microsoft.graph.conflictBehavior': 'rename'
                                }
                                requests.post(folder_endpoint_2, json=fd, headers=headers)
                            


                        else:
                            print(f"Failed to create folder. Status code: {response.status_code}, Response: {response.text}")

                        print('Step 5, Companies Stored Data:', company_stored_data)

                        #update link onto bitrix 24

                        sleep(2)

                        #Headers_2 = {
                        #    'ID': str(extracted_data['ID']),
                        #    'FIELDS[UF_CRM_1680267368623][0]': access_link
                        #}

                        #print(Headers_2)

                        encoded_access_link = urllib.parse.quote(access_link)

                        URI_ENDPOINT = f"https://rtech.bitrix24.com/rest/1/n0nai3kd6jtjp6ak//crm.lead.update.json?ID={extracted_data['ID']}&FIELDS[UF_CRM_1680267368623][0]={encoded_access_link}"

                        response = requests.post(URI_ENDPOINT)

                        if response.status_code == 200:
                            print (f'Step 7, link : {access_link}  updated successfully in Bitrix 24')

                        else: 
                            print(f'failed at last stage ie. updation, Response: {response.text}, Status code: {response.status_code}')


                        print()
                        print()

                        

                return jsonify({"message": "Webhook triggered successfully", "stored_data": stored_data}), 200
            else:
                return jsonify({"error": "Webhook trigger failed"}),  
        else:
            return jsonify({"error": "Required field not found"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9852, debug=False)
