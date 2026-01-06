import requests
from getpass import getpass


auth_endpoint = "http://localhost:8000/api/auth/token/"
# username = input("What is your username? \n")
# password = getpass("What is your password? \n")

auth_response = requests.post(auth_endpoint, json={'email': 'abasskoyang05@gmail.com', 'password': 'Koyang12345'})
print(auth_response.json());

if auth_response.status_code == 200:
    token = auth_response.json()['access']
    headers = {
        "Authorization": f"Bearer {token}"
    }

    endpoint = "http://localhost:8000/api/comments/1/replies/"

    response = requests.get(endpoint, headers=headers);
    print(response.json())