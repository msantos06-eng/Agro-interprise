import sqlite3

def conectar():
    return sqlite3.connect("database.db", check_same_thread=False)

def criar_tabelas():
    conn = conectar()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT UNIQUE,
            password TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS fazendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            user TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS talhoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            user TEXT
        )
    """)

    conn.commit()
    conn.close()