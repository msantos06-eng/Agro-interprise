import requests

API_URL = "https://SEU-BACKEND.onrender.com"

def login(email, password):
    return requests.post(f"{API_URL}/auth/login", json={
        "email": email,
        "password": password
    }).json()