import streamlit as st
import sqlite3
import hashlib
import os
import requests
import numpy as np
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw
from PIL import Image
import io

st.set_page_config(layout="wide")

# =========================
# DB
# =========================
conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, email TEXT, senha TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS talhoes (id INTEGER PRIMARY KEY, usuario_id INTEGER, geojson TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS fazendas (id INTEGER PRIMARY KEY, usuario_id INTEGER, nome TEXT)")
conn.commit()

# =========================
# FUNÇÕES
# =========================
def hash_senha(s):
    return hashlib.sha256(s.encode()).hexdigest()

def gerar_taxa(ndvi):
    if ndvi < 0.3:
        return 150
    elif ndvi < 0.6:
        return 120
    else:
        return 80

def get_token():
    url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

    data = {
        "grant_type": "client_credentials",
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET")
    }

    r = requests.post(url, data=data)
    return r.json()["access_token"]

@st.cache_data(ttl=3600)
def buscar_ndvi_satellite(geojson):
    token = get_token()

    url = "https://sh.dataspace.copernicus.eu/api/v1/process"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = {
        "input": {
            "bounds": {
                "geometry": geojson
            },
            "data": [{"type": "sentinel-2-l2a"}]
        },
        "evalscript": """
        //VERSION=3
        function setup() {
          return {
            input: ["B04", "B08"],
            output: { bands: 3 }
          };
        }

        function evaluatePixel(sample) {
          let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);

          if (ndvi < 0.2) return [1, 0, 0];
          else if (ndvi < 0.5) return [1, 1, 0];
          else return [0, 1, 0];
        }
        """,
        "output": {"width": 512, "height": 512}
    }

    response = requests.post(url, headers=headers, json=body)
    return response.content

# =========================
# LOGIN
# =========================
st.sidebar.title("Login")

email = st.sidebar.text_input("Email")
senha = st.sidebar.text_input("Senha", type="password")

if st.sidebar.button("Entrar"):
    senha_hash = hash_senha(senha)
    c.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, senha_hash))
    user = c.fetchone()

    if user:
        st.session_state["user_id"] = user[0]
        st.success("Logado!")
    else:
        st.error("Erro login")

if st.sidebar.button("Cadastrar"):
    senha_hash = hash_senha(senha)
    c.execute("SELECT * FROM usuarios WHERE email=?", (email,))
    if c.fetchone():
        st.error("Usuário já existe")
    else:
        c.execute("INSERT INTO usuarios (email, senha) VALUES (?,?)", (email, senha_hash))
        conn.commit()
        st.success("Usuário criado!")

# =========================
# FAZENDA
# =========================
if "user_id" in st.session_state:
    st.sidebar.subheader("Fazendas")

    nome_fazenda = st.sidebar.text_input("Nome da fazenda")

    if st.sidebar.button("Criar Fazenda"):
        c.execute("INSERT INTO fazendas (usuario_id, nome) VALUES (?, ?)",
                  (st.session_state["user_id"], nome_fazenda))
        conn.commit()
        st.sidebar.success("Fazenda criada")

# =========================
# MENU
# =========================
menu = st.sidebar.radio("Menu", ["Dashboard", "Mapa", "NDVI Satélite"])

# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":
    st.title("📊 Dashboard")

    if "user_id" not in st.session_state:
        st.warning("Faça login")
    else:
        c.execute("SELECT COUNT(*) FROM talhoes WHERE usuario_id=?", (st.session_state["user_id"],))
        total = c.fetchone()[0]

        st.metric("🌾 Total de Talhões", total)

# =========================
# MAPA
# =========================
if menu == "Mapa":
    mapa = folium.Map(location=[-12.5, -45.0], zoom_start=13)
    Draw(export=True).add_to(mapa)

    map_data = st_folium(mapa)

    if map_data and map_data.get("last_active_drawing"):
        geojson = map_data["last_active_drawing"]
        st.session_state["talhao"] = geojson

        if "user_id" in st.session_state:
            if st.button("Salvar Talhão"):
                c.execute(
                    "INSERT INTO talhoes (usuario_id, geojson) VALUES (?, ?)",
                    (st.session_state["user_id"], str(geojson))
                )
                conn.commit()
                st.success("Talhão salvo!")

# =========================
# NDVI SATÉLITE
# =========================
if menu == "NDVI Satélite":

    if "talhao" not in st.session_state:
        st.warning("Desenhe um talhão primeiro")
    else:
        st.info("Buscando imagem...")

        geo = st.session_state["talhao"]["geometry"]

        with st.spinner("Processando..."):
            img_bytes = buscar_ndvi_satellite(geo)

        imagem = Image.open(io.BytesIO(img_bytes))
        st.image(imagem, caption="NDVI Satélite")