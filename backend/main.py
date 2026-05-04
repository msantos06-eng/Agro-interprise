from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

from db import SessionLocal
from models.user import User
from models.farm import Farm
from auth.jwt_handler import create_token, verify_token
from rules import pode_criar_talhao

app = FastAPI(title="Agro-interprise API", version="1.0.0")

# ─────────────────────────────────────────
# CORS (ajuste as origens conforme necessário)
# ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, substitua por domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────
# HASH DE SENHA
# ─────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ─────────────────────────────────────────
# SCHEMAS PYDANTIC (validação de entrada)
# ─────────────────────────────────────────
class AuthSchema(BaseModel):
    email: EmailStr
    password: str


class FarmSchema(BaseModel):
    name: str


# ─────────────────────────────────────────
# DEPENDÊNCIAS
# ─────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token mal formatado")

    token = authorization.removeprefix("Bearer ")
    data = verify_token(token)

    if not data or "user_id" not in data:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    user = db.query(User).filter(User.id == data["user_id"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    return user


# ─────────────────────────────────────────
# HEALTHCHECK
# ─────────────────────────────────────────
@app.get("/ping", tags=["Health"])
def ping():
    return {"status": "ok"}


# ─────────────────────────────────────────
# AUTENTICAÇÃO
# ─────────────────────────────────────────
@app.post("/login", tags=["Auth"])
def login(data: AuthSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    # Verifica usuário e senha com hash — sem vazar qual dos dois falhou
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = create_token(user.id)
    return {"token": token}


@app.post("/register", tags=["Auth"])
def register(data: AuthSchema, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),  # ✅ Senha hasheada com bcrypt
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(user.id)
    return {"token": token}


# ─────────────────────────────────────────
# USUÁRIO
# ─────────────────────────────────────────
@app.get("/me", tags=["User"])
def get_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "plan": user.plan,
        "trial_end": user.trial_end,
        "expires_at": user.expires_at,
    }


# ─────────────────────────────────────────
# FAZENDAS
# ─────────────────────────────────────────
@app.get("/farms", tags=["Farms"])
def get_farms(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    farms = db.query(Farm).filter(Farm.user_id == user.id).all()
    return [{"id": f.id, "name": f.name} for f in farms]


@app.post("/farms", tags=["Farms"])
def create_farm(
    data: FarmSchema,  # ✅ Nome vem do body agora, não da query string
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not pode_criar_talhao(user, db):
        raise HTTPException(status_code=403, detail="Limite do plano atingido")

    farm = Farm(name=data.name, user_id=user.id)
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return {"id": farm.id, "name": farm.name}