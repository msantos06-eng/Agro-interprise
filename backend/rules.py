from sqlalchemy.orm import Session

LIMITES_PLANO = {
    "free": 1,
    "trial": 3,
    "pro": 999
}

def pode_criar_talhao(user, db: Session) -> bool:
    from models.farm import Farm
    limite = LIMITES_PLANO.get(user.plan, 1)
    total = db.query(Farm).filter(Farm.user_id == user.id).count()
    return total < limite
