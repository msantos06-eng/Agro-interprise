import mercadopago
from datetime import datetime, timedelta
from db import SessionLocal
from models import User
import os

sdk = mercadopago.SDK(os.getenv("MP_ACCESS_TOKEN"))


def criar_pagamento(user_id):
    pref = {
        "items": [
            {
                "title": "Plano AgroForce",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 49.90
            }
        ],
        "metadata": {
            "user_id": user_id
        }
    }

    res = sdk.preference().create(pref)
    return res["response"]["init_point"]


def ativar_plano(user_id):
    db = SessionLocal()

    user = db.query(User).filter(User.id == user_id).first()

    user.plan = "mensal"
    user.expires_at = datetime.utcnow() + timedelta(days=30)

    db.commit()
    db.close()