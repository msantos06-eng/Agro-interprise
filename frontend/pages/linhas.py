import streamlit as st
import json
from shapely.geometry import shape, mapping
import folium
from streamlit_folium import st_folium

from utils.geo_utils import generate_planting_lines
from utils.export_utils import export_geojson

# =========================
# UI
# =========================
st.set_page_config(page_title="Linhas de Plantio", layout="wide")
st.title("🌱 Linhas de Plantio")

# =========================
# UPLOAD
# =========================
uploaded_file = st.file_uploader("📂 Envie o GeoJSON do talhão", type=["geojson", "json"])

if uploaded_file:
    data = json.load(uploaded_file)

    # pegar primeira geometria
    geom = shape(data["features"][0]["geometry"])

    st.success("Talhão carregado!")

    # =========================
    # CONFIG
    # =========================
    spacing = st.slider("Espaçamento entre linhas (graus)", 0.0001, 0.005, 0.0005)

    # =========================
    # GERAR LINHAS
    # =========================
    if st.button("🚜 Gerar Linhas"):
        lines = generate_planting_lines(geom, spacing)

        st.success(f"{len(lines)} linhas geradas!")

        # =========================
        # MAPA
        # =========================
        center = geom.centroid
        m = folium.Map(location=[center.y, center.x], zoom_start=15)

        folium.GeoJson(mapping(geom), name="Talhão").add_to(m)

        for line in lines:
            folium.GeoJson(
                mapping(line),
                style_function=lambda x: {"color": "green", "weight": 2}
            ).add_to(m)

        st_folium(m, width=1000, height=500)

        # =========================
        # EXPORT
        # =========================
        features = [{"geometry": l} for l in lines]
        geojson_data = export_geojson(features)

        # ✅ BOTÃO TEM QUE FICAR AQUI DENTRO
        st.download_button(
            "📥 Baixar Linhas (GeoJSON)",
            json.dumps(geojson_data, indent=2),
            file_name="linhas_plantio.geojson",
            mime="application/json"
        )

else:
    st.info("Envie um GeoJSON para começar")