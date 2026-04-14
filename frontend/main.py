from fastapi import FastAPI
import numpy as np
from ndvi import calculate_ndvi
from ai import analyze_ndvi
from db import SessionLocal
from models import Farm

app = FastAPI()

@app.get("/farms")
def get_farms():

    db = SessionLocal()

    try:
        farms = db.query(Farm).all()

        return [
            {"id": f.id, "name": f.name}
            for f in farms
        ]

    finally:
        db.close()

app = FastAPI()

@app.get("/login")
def login():
    return {"token": "fake-jwt-token"}

@app.get("/ndvi")
def ndvi():

    red = np.random.rand(50,50)
    nir = np.random.rand(50,50)

    ndvi = calculate_ndvi(red, nir)

    status, recommendation = analyze_ndvi(ndvi)

    return {
        "status": status,
        "recommendation": recommendation,
        "mean_ndvi": float(ndvi.mean())
    }