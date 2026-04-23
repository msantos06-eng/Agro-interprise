import streamlit as st
import sys
import os
import json
import requests
import json
import numpy as np
import pandas as pd
import streamlit as st
import streamlit as st

# 🔗 API (OBRIGATÓRIO PRIMEIRO)
API = "https://agroforce-production.up.railway.app"

st.write("API REAL:", API)

# 🚫 bloqueio sem login
def tela_login():
    import streamlit as st
    st.write("Login")

if not st.session_state.get("token"):
    tela_login()
    st.stop()

# 🔐 sessão
if "token" not in st.session_state:
    st.session_state.token = None

# 🔐 headers
def get_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }

def tela_login():
    st.title("AgroForce")

    aba = st.radio("Escolha", ["Login", "Cadastro"])

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    # 🔐 LOGIN
    if aba == "Login":
        if st.button("Entrar"):
            try:
                r = requests.post(
                    f"{API}/login",
                    json={"email": email, "password": senha}
                )

                if r.status_code == 200:
                    st.session_state.token = r.json()["token"]
                    st.success("Login realizado!")
                    st.rerun()
                else:
                    st.error("Login inválido")

            except Exception as e:
                st.error(f"Erro: {e}")

    # 🆕 CADASTRO
    if aba == "Cadastro":
        if st.button("Cadastrar"):
            try:
                r = requests.post(
                    f"{API}/register",
                    json={"email": email, "password": senha}
                )

                if r.status_code == 200:
                    st.session_state.token = r.json()["token"]
                    st.success("Conta criada!")
                    st.rerun()
                    
                else:
                        st.error("Erro ao cadastrar")
                        st.write("STATUS:", r.status_code)
                        st.write("RESPOSTA:", r.text)

            except Exception as e:
                st.error(f"Erro: {e}")

# 📊 dados usuário
@st.cache_data(ttl=30)
def get_user_data():
    r = requests.get(f"{API}/me", headers=get_headers())
    return r.json()

user_data = get_user_data()

# ⚙️ config
st.set_page_config(page_title="AgroForce", layout="wide", page_icon="🌾")

# 📊 sidebar
st.sidebar.title("Conta")

plano = user_data.get("plan", "free")

if plano == "free":
    st.sidebar.warning("Plano FREE")

if user_data.get("trial_end"):
        st.sidebar.caption(f"Trial até: {user_data['trial_end']}")

    # contador de uso
try:
    farms = requests.get(f"{API}/farms", headers=get_headers()).json()
    st.sidebar.caption(f"{len(farms)}/3 talhões usados")
    st.sidebar.progress(min(len(farms) / 3, 1.0))
except:
       pass

    # 🚀 BOTÃO DE UPGRADE (AQUI É O CERTO)
if plano == "free":
    if st.sidebar.button("🚀 Fazer Upgrade"):
        r = requests.get(
            f"{API}/create-payment-link",
            headers=get_headers()
        )

        st.write("STATUS:", r.status_code)
        st.write("TEXTO:", r.text)

        try:
            data = r.json()
        except:
            st.error("Erro ao converter resposta da API")
            st.stop()

        if "url" in data:
            link = data["url"]
            st.sidebar.markdown(f"[💳 Pagar agora]({link})")
        else:
            st.error("Erro ao gerar link de pagamento")
else:
    st.sidebar.success(f"Plano {plano.upper()}")
# 🔓 logout primeiro
if st.sidebar.button("Sair"):
    st.session_state.pop("token", None)
    st.rerun()
    st.write("TOKEN:", st.session_state.get("token"))

st.markdown("Selecione uma funcionalidade no menu lateral")

# 🧠 funções utilitárias
def talhao_ativo():
    t = st.session_state.get("talhoes", [])
    i = st.session_state.get("idx_ativo", 0)
    if t and 0 <= i < len(t):
        return t[i]
    return None

def status_plano():
    import datetime

def verificar_plano(plano):
    if plano == "free":
        return "free"
    else:
        return "ativo"

if user_data["expires_at"] is None:
        status = "ativo"
if datetime.datetime.utcnow().isoformat() > user_data["expires_at"]:
    status = "expirado"
status = "ativo"

# ── Tabs ─────────────────────────────────────────────
tabs = st.tabs([
    "🗺️ Talhões",
    "🔵 Buffer",
    "📊 NDVI / Grade",
    "🎯 Taxa Variável",
    "🌾 Proj. de Linha",
    "📤 Exportar",
])
