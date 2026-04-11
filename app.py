# ======================================
# AGRO SAAS ENTERPRISE (NÍVEL EMPRESA)
# ======================================

import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import plotly.express as px
import datetime

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Agro SaaS Enterprise", layout="wide")

# =========================
# DATABASE
# =========================
def get_conn():
    return sqlite3.connect("agro.db", check_same_thread=False)

conn = get_conn()
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT, plan TEXT, stripe_id TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS farms (id INTEGER PRIMARY KEY, user_id INTEGER, name TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS fields (id INTEGER PRIMARY KEY, farm_id INTEGER, name TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS ndvi (id INTEGER PRIMARY KEY, user_id INTEGER, value REAL, date TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS subscriptions (id INTEGER PRIMARY KEY, user_id INTEGER, status TEXT, plan TEXT, renew_date TEXT)")
conn.commit()

# =========================
# AUTH
# =========================
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()


def login(email, password):
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, hash_password(password)))
    return c.fetchone()


def register(email, password):
    try:
        c.execute("INSERT INTO users (email, password, plan) VALUES (?, ?, 'Free')", (email, hash_password(password)))
        conn.commit()
        return True
    except:
        return False

# =========================
# SESSION
# =========================
if "user" not in st.session_state:
    st.session_state.user = None

# =========================
# LOGIN UI
# =========================
if st.session_state.user is None:
    st.title("🚀 Agro SaaS Enterprise")

    tab1, tab2 = st.tabs(["Login", "Cadastro"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            user = login(email, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Erro no login")

    with tab2:
        email = st.text_input("Novo Email")
        password = st.text_input("Nova Senha", type="password")
        if st.button("Cadastrar"):
            if register(email, password):
                st.success("Conta criada")

# =========================
# APP
# =========================
else:
    user = st.session_state.user
    user_id = user[0]
    plan = user[3]

    st.sidebar.title("🌾 Agro SaaS Enterprise")
    st.sidebar.markdown(f"Plano: **{plan}**")

    menu = st.sidebar.radio("Menu", ["Dashboard", "NDVI", "Fazendas", "Talhões", "Assinatura", "Admin", "Logout"])

    if menu == "Logout":
        st.session_state.user = None
        st.rerun()

    # =========================
    # DASHBOARD
    # =========================
    if menu == "Dashboard":
        st.title("📊 Analytics SaaS")

        farms = pd.read_sql_query("SELECT COUNT(*) as total FROM farms WHERE user_id=?", conn, params=(user_id,))
        fields = pd.read_sql_query("SELECT COUNT(*) as total FROM fields WHERE farm_id IN (SELECT id FROM farms WHERE user_id=?)", conn, params=(user_id,))
        ndvi = pd.read_sql_query("SELECT AVG(value) as avg FROM ndvi WHERE user_id=?", conn, params=(user_id,))

        col1, col2, col3 = st.columns(3)
        col1.metric("Fazendas", int(farms['total'][0]))
        col2.metric("Talhões", int(fields['total'][0]))
        col3.metric("NDVI Médio", round(ndvi['avg'][0],2) if ndvi['avg'][0] else 0)

        df = pd.read_sql_query("SELECT date, value FROM ndvi WHERE user_id=?", conn, params=(user_id,))
        if not df.empty:
            fig = px.line(df, x="date", y="value", title="NDVI ao longo do tempo")
            st.plotly_chart(fig, use_container_width=True)

    # =========================
    # NDVI
    # =========================
    elif menu == "NDVI":
        st.title("🛰️ NDVI Inteligente")

        if plan == "Free":
            st.warning("Plano Free limitado")

        value = st.slider("NDVI", 0.0, 1.0, 0.6)
        if st.button("Salvar"):
            c.execute("INSERT INTO ndvi (user_id, value, date) VALUES (?, ?, ?)", (user_id, value, str(datetime.date.today())))
            conn.commit()

    # =========================
    # SUBSCRIPTION
    # =========================
    elif menu == "Assinatura":
        st.title("💳 Gestão de Assinatura")

        sub = pd.read_sql_query("SELECT * FROM subscriptions WHERE user_id=?", conn, params=(user_id,))

        if sub.empty:
            st.info("Sem assinatura ativa")
        else:
            st.dataframe(sub)

        if st.button("Simular renovação"):
            next_date = str(datetime.date.today() + datetime.timedelta(days=30))
            c.execute("INSERT INTO subscriptions (user_id, status, plan, renew_date) VALUES (?, 'active', ?, ?)",
                      (user_id, plan, next_date))
            conn.commit()
            st.success("Assinatura atualizada")

    # =========================
    # ADMIN
    # =========================
    elif menu == "Admin":
        st.title("👨‍💼 Painel Admin")

        users = pd.read_sql_query("SELECT id, email, plan FROM users", conn)
        st.dataframe(users)

        subs = pd.read_sql_query("SELECT * FROM subscriptions", conn)
        st.dataframe(subs)

        st.subheader("📊 Receita estimada")
        revenue = len(subs) * 49
        st.metric("MRR (R$)", revenue)

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("Agro SaaS Enterprise • Plataforma Escalável 🚀")