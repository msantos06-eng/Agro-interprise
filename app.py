import streamlit as st
import sqlite3
import hashlib
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw
import numpy as np
import geopandas as gpd
from shapely.geometry import shape
import rasterio
import tempfile
import os
import zipfile
import requests
import json

st.set_page_config(layout="wide")

# =========================
# DB
# =========================
conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, email TEXT, senha TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS talhoes (id INTEGER PRIMARY KEY, usuario_id INTEGER, geojson TEXT)")
conn.commit()

# =========================
# FUNÇÕES
# =========================
def hash_senha(s):
         return
         hashlib.sha256(s.encode()).hexdigest()


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
        "client_id": "sh-c0dac085-be43-4a1a-846b-9f2007c39719",
        "client_secret": "mquL3Z5gSzNGH8Dq4eAynUuczrC7P5UE"
    }

    r = requests.post(url, data=data)
    return r.json()["access_token"]


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
            "data": [{
                "type": "sentinel-2-l2a"
            }]
        },
        "evalscript": """
        return [ (B08 - B04) / (B08 + B04) ];
        """,
        "output": {
            "width": 512,
            "height": 512
        }
    }

    response = requests.post(url, headers=headers, json=body)
    return response.content
    elif ndvi < 0.6:
        return 120
    else:
        return 80

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
    c.execute("INSERT INTO usuarios (email, senha) VALUES (?,?)", (email, senha_hash))
    conn.commit()
    st.success("Usuário criado!")

# =========================
# MENU
# =========================
menu = st.sidebar.radio("Menu", [
    "Mapa",
    "NDVI",
    "NDVI Satélite",
    "Exportar"
])
if menu == "NDVI Satélite":

    if "talhao" not in st.session_state:
        st.warning("Desenhe um talhão primeiro")
    else:
        st.info("Buscando satélite...")

        geo = st.session_state["talhao"]["geometry"]

        img_bytes = buscar_ndvi_satellite(geo)

        from PIL import Image
        import io

        imagem = Image.open(io.BytesIO(img_bytes))

        st.image(imagem, caption="NDVI Satélite")

# =========================
# MAPA
# =========================
if menu == "Mapa":
    mapa = folium.Map(location=[-12.5, -45.0], zoom_start=13)

    Draw(export=True).add_to(mapa)

    map_data = st_folium(mapa)

    if map_data and map_data.get("last_active_drawing"):
        geojson = map_data["last_active_drawing"]

        if "user_id" in st.session_state:
            c.execute("INSERT INTO talhoes (usuario_id, geojson) VALUES (?,?)",
                      (st.session_state["user_id"], str(geojson)))
            conn.commit()
            st.success("Talhão salvo!")

# =========================
# NDVI + IA
# =========================
if menu == "NDVI":
    arquivo = st.file_uploader("Upload TIF", type=["tif"])

    if arquivo:
        with rasterio.open(arquivo) as src:
            img = src.read()

        nir = img[3].astype(float)
        red = img[2].astype(float)

        ndvi = (nir - red) / (nir + red + 0.01)

        st.image(ndvi, caption="NDVI")

        taxa = np.vectorize(gerar_taxa)(ndvi)

        st.image(taxa, caption="Taxa Variável")

        st.session_state["taxa"] = taxa

# =========================
# EXPORTAR
# =========================
if menu == "Exportar":

    if "user_id" not in st.session_state:
        st.warning("Faça login")
    else:
        c.execute("SELECT geojson FROM talhoes WHERE usuario_id=?", (st.session_state["user_id"],))
        dados = c.fetchall()

        if dados:
            geojson = eval(dados[-1][0])
            geom = shape(geojson["geometry"])

            gdf = gpd.GeoDataFrame({
                "taxa": [120]
            }, geometry=[geom], crs="EPSG:4326")

            tmp = tempfile.mkdtemp()
            shp = os.path.join(tmp, "mapa.shp")
            gdf.to_file(shp)

            # ISOXML
            xml_path = os.path.join(tmp, "taskdata.xml")
            with open(xml_path, "w") as f:
                f.write("<ISO11783_TaskData></ISO11783_TaskData>")

            zip_path = os.path.join(tmp, "export.zip")
            with zipfile.ZipFile(zip_path, 'w') as z:
                for file in os.listdir(tmp):
                    z.write(os.path.join(tmp, file), file)

            with open(zip_path, "rb") as f:
                st.download_button("Baixar para máquina", f, file_name="mapa.zip")

            st.success("Exportado!")