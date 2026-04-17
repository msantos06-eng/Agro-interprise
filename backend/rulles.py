import datetime

def pode_criar_talhao(user, db):
    now = datetime.datetime.utcnow()

    if user.plan == "free":
        if now > user.trial_end:
            return False

        total = db.query(Farm).filter(Farm.user_id == user.id).count()

        if total >= 3:
            return False

    else:
        if user.expires_at and now > user.expires_at:
            return False

    return True