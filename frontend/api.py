import requests

API_URL = "https:agroforce-production.up.railway.app"

def login(email, password):
    return requests.post(f"{API_URL}/auth/login", json={
        "email": email,
        "password": password
    }).json()