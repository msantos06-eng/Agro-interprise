import jwt
import datetime
from fastapi import HTTPException

SECRET = "SUPER_SECRET_KEY"

def create_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")


def verify_token(token):
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")