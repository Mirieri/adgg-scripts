import json
import pdfkit
import requests
from jinja2 import Environment, FileSystemLoader

# Define Animal API endpoint
animal_endpoint = "https://www.rest.adgg.ilri.org/dev/api/animals"

# Define API endpoint and credentials
user_credential_endpoint = "https://www.rest.adgg.ilri.org/dev/authentication_token"
username = "admin"
password = "Scooby@2021"

# Set headers 
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

# Set payload for request
payload = {"username": username, "password": password}

# Call the API using Requests and retrieve authentication token
auth_response = requests.post(user_credential_endpoint, data=json.dumps(payload), headers=headers)

if auth_response.status_code == 200:
    response_json = json.loads(auth_response.text)
    access_token = response_json.get('access_token')
    if access_token:
        print("Authentication successful.")
    else:
        print("Access token not found in response.")
else:
    print(f"Error calling API. Status code: {auth_response.status_code}. Response text: {auth_response.text}")

# # Initializing access_token variable
# access_token = None

if auth_response.status_code == 200 and access_token:
    # Set headers using the authentication token
    headers = {
        'accept': 'application/ld+json',
        'Authorization': f'Bearer {access_token}'
    }

    # Define Animal API endpoint
    endpoint_animal = "https://www.rest.adgg.ilri.org/dev/api/animals"

    # Call the API to retrieve animal data
    response = requests.get(f"{endpoint_animal}?page=1&pagination=false", headers=headers)

    if response.status_code == 200 and len(response.text) > 0:
        # Parse the response as JSON
        data = json.loads(response.text)

        # Creating a dictionary for nodes
        nodes = {}

        # Creating a list of links
        links = []

        # Finding the Relationship between the members and appending to node and link lists
        for member in data['hydra:member']:
            node = {"id": member['id'], "name": member['name']}
            nodes[member['id']] = node
            if member.get('sireId'):
                links.append({"source": member['sireId'], "target": member['id']})
            if member.get('damId'):
                links.append({"source": member['damId'], "target": member['id']})

        # Finding the root node
        root = None
        for node_id in nodes:
            if not any(link['target'] == node_id for link in links):
                root = node_id
                break

        # Create the tree layout using a recursive function
        tree = {"name": "", "children": []}


        def find_children(parent):
            children = []
            for link in links:
                if link['source'] == parent:
                    child = nodes[link['target']]
                    child_tree = {"name": child['name']}
                    if link['target'] in nodes:
                        child_tree['children'] = find_children(link['target'])
                    children.append(child_tree)
            return children


        tree['children'] = find_children(root)

        # Render the template with the tree data
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template("template.html")
        html = template.render(tree=tree)

        # Convert HTML to PDF using pdfkit
        pdfkit.from_string(html, 'output.pdf')

    else:
        print(f"Error calling API. Status code: {response.status_code}. Response text: {response.text}")

else:
    print(f"Authentication failed. Status code: {auth_response.status_code}")
