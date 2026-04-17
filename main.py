from fastapi import FastAPI, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from db import SessionLocal
from models import Farm, User
from auth import verify_token
from rules import pode_criar_talhao
from fastapi import Body
from models.user import User
from auth.jwt_handler import create_token


@app.post("/login")
def login(data: dict = Body(...), db: Session = Depends(get_db)):
    email = data.get("email")
    password = data.get("password")
@app.get("/me")
def get_me(user: User = Depends(get_user)):
    return {
        "plan": user.plan,
        "trial_end": user.trial_end,
        "expires_at": user.expires_at
    }

    user = db.query(User).filter(User.email == email).first()

    if not user or user.hashed_password != password:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = create_token(user.id)

    return {"token": token}

app = FastAPI()

import requests

API = "https://SEU_BACKEND.up.railway.app"

def tela_login():
    st.title("Login")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        r = requests.post(
            f"{API}/login",
            json={"email": email, "password": senha}
        )

        if r.status_code == 200:
            st.session_state.token = r.json()["token"]
            st.rerun()
        else:
            st.error("Login inválido")
            from fastapi import Body
from models.user import User
from auth.jwt_handler import create_token
from sqlalchemy.orm import Session
from database import SessionLocal


@app.post("/register")
def register(data: dict = Body(...), db: Session = Depends(get_db)):
    email = data.get("email")
    password = data.get("password")

    # verificar se já existe
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    user = User(
        email=email,
        hashed_password=password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(user.id)

    return {"token": token}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user(authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    data = verify_token(token)

    user = db.query(User).filter(User.id == data["user_id"]).first()

    if not user:
        raise HTTPException(status_code=401)

    return user


@app.get("/farms")
def get_farms(user: User = Depends(get_user), db: Session = Depends(get_db)):
    farms = db.query(Farm).filter(Farm.user_id == user.id).all()

    return [{"id": f.id, "name": f.name} for f in farms]


@app.post("/farms")
def create_farm(name: str, user: User = Depends(get_user), db: Session = Depends(get_db)):

    if not pode_criar_talhao(user, db):
        raise HTTPException(status_code=403, detail="Limite do plano atingido")

    farm = Farm(name=name, user_id=user.id)

    db.add(farm)
    db.commit()
    db.refresh(farm)

    return {"id": farm.id, "name": farm.name}