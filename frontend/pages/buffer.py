import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import mapping

from utils.geo_utils import generate_buffer
from utils.export_utils import export_geojson


def render_buffer():

    st.header("🔵 Buffer")

    # ---------------- VALIDAÇÃO ----------------
    if "talhoes" not in st.session_state or not st.session_state.talhoes:
        st.info("Crie um talhão primeiro")
        return

    if "idx_ativo" not in st.session_state:
        st.session_state.idx_ativo = 0

    ta = st.session_state.talhoes[st.session_state.idx_ativo]

    st.subheader(f"Talhão: {ta.get('nome', 'Sem nome')}")

    # ---------------- CONFIG ----------------
    dist = st.slider("Distância do buffer (metros)", 5, 100, 20)

    # ---------------- GERAR BUFFER ----------------
    if st.button("Gerar buffer"):
        try:
            geom = ta.get("geom")

            if not geom:
                st.error("Talhão sem geometria")
                return

            buffer_geom = generate_buffer(geom, dist)

            ta["buffer_geom"] = buffer_geom
            st.success("Buffer gerado com sucesso!")

        except Exception as e:
            st.error(f"Erro ao gerar buffer: {e}")

    # ---------------- MAPA ----------------
    if ta.get("geom"):
        m = folium.Map(location=[-15, -47], zoom_start=5)

        # talhão
        folium.GeoJson(mapping(ta["geom"]), name="Talhão").add_to(m)

        # buffer
        if ta.get("buffer_geom"):
            folium.GeoJson(
                mapping(ta["buffer_geom"]),
                name="Buffer",
                style_function=lambda x: {
                    "color": "blue",
                    "fillOpacity": 0.2,
                },
            ).add_to(m)

        st_folium(m, width=700, height=500)

    # ---------------- EXPORT ----------------
    if ta.get("buffer_geom"):
        geojson = export_geojson(
            [{"geometry_wgs84": ta["buffer_geom"]}],
            properties=[]
        )

        st.download_button(
            "⬇️ Baixar Buffer (GeoJSON)",
            data=geojson,
            file_name="buffer.geojson",
            mime="application/json"
        )