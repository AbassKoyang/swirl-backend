import requests


endpoint = "https://swirl-backend-n3t8.onrender.com/api/categories/"

name = input("Name: ")
slug = input("Slug: ")
data = {
    'name': name,
    'slug': slug,
}
response = requests.post(endpoint, json=data);