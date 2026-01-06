from shlex import join
import requests
from getpass import getpass


auth_endpoint = "http://localhost:8000/api/auth/token/"
# email = input("What is your email? \n")
# password = getpass("What is your password? \n")
title = input("Enter post title \n")
content = input("Enter cotent \n")
slug = input("Enter slug \n")

auth_response = requests.post(auth_endpoint, json={'email': 'abasskoyang05@gmail.com', 'password': 'Koyang12345'})
print(auth_response.json());
token = auth_response.json()['access']
headers = {
    "Authorization": f"Bearer {token}"
}

endpoint = "http://localhost:8000/api/posts/"

data = {
    'title': title,
    'content': content,
    'category_id': 1,
    'slug': slug
}
response = requests.post(endpoint, headers=headers, json=data);
print(response.json())
# print(response.text)
# print(response.status_code)