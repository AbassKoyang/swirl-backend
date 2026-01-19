import requests


endpoint = "http://localhost:8000/api/categories/"

data = {
    'name': 'Programming',
    'slug': 'programming',
}
response = requests.post(endpoint, json=data);