import hashlib
from database import conectar

def hash_senha(password):
    return hashlib.sha256(password.encode()).hexdigest()

def cadastrar(user, password):
    conn = conectar()
    c = conn.cursor()

    senha_hash = hash_senha(password)

    try:
        c.execute("INSERT INTO users (user, password) VALUES (?,?)", (user, senha_hash))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def login(user, password):
    conn = conectar()
    c = conn.cursor()

    senha_hash = hash_senha(password)

    c.execute("SELECT * FROM users WHERE user=? AND password=?", (user, senha_hash))
    result = c.fetchone()

    conn.close()
    return result is not None