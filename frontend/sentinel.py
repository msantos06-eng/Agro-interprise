import requests

def get_token(client_id, client_secret):

    url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

    data = {
        "grant_type": "client_credentials",
        "sh-c0dac085-be43-4a1a-846b-9f2007c39719": client_id,
        "mquL3Z5gSzNGH8Dq4eAynUuczrC7P5UE": client_secret
    }

    r = requests.post(url, data=data)
    return r.json()["access_token"]