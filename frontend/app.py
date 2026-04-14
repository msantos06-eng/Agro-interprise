import streamlit as st
import json
import folium

from folium.plugins import Draw, MeasureControl
from streamlit_folium import st_folium
from shapely.geometry import mapping

from export_utils import export_geojson, export_kml, export_shapefile, brand_package
from geo_utils import (
    geojson_to_shapely,
    generate_buffer,
    compute_field_stats
)

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="AgroForce", layout="wide")

info = brand_package()
st.title(info["app_name"])
st.caption(f"Versão {info['version']} - {info['status']}")

# =========================
# SESSION STATE
# =========================

default_keys = [
    'field_geom', 'grid_cells', 'vra_cells',
    'lines', 'buffer_geom'
]

for k in default_keys:
    if k not in st.session_state:
        st.session_state[k] = None

# =========================
# SIDEBAR
# =========================

with st.sidebar:
    st.title("🌾 AgroForce")

    if st.session_state.field_geom:
        stats = compute_field_stats(st.session_state.field_geom)
        st.success("Talhão ativo")
        st.metric("Área", f"{stats['area_ha']:.2f} ha")
        st.metric("Perímetro", f"{stats['perimeter_m']:.2f} m")
    else:
        st.warning("Sem talhão")

# =========================
# TABS
# =========================

tabs = st.tabs([
    "🗺️ Talhão",
    "🔵 Buffer",
    "📤 Exportar"
])

# =========================
# TAB 1 - TALHÃO
# =========================

with tabs[0]:

    st.header("Desenho do Talhão")

    col1, col2 = st.columns([3, 1])

    with col1:

        center = [-15, -52]
        zoom = 5

        if st.session_state.field_geom:
            c = st.session_state.field_geom.centroid
            center = [c.y, c.x]
            zoom = 14

        m = folium.Map(location=center, zoom_start=zoom)
        folium.TileLayer("OpenStreetMap").add_to(m)
        folium.TileLayer("Esri.WorldImagery").add_to(m)

        MeasureControl().add_to(m)

        if st.session_state.field_geom:
            folium.GeoJson(mapping(st.session_state.field_geom)).add_to(m)

        Draw(
            draw_options={
                "polygon": True,
                "rectangle": True,
                "polyline": False,
                "circle": False,
                "marker": False
            },
            edit_options={"edit": True}
        ).add_to(m)

        out = st_folium(m, height=520, key="map")

    with col2:

        st.subheader("Ações")

        if st.button("Salvar Talhão"):

            drawings = (out or {}).get("all_drawings") or []
            if drawings:

                geom = geojson_to_shapely(drawings[-1])

                st.session_state.field_geom = geom

                for k in default_keys:
                    if k != "field_geom":
                        st.session_state[k] = None

                st.success("Salvo!")
                st.rerun()

        st.divider()

        uploaded = st.file_uploader("Importar GeoJSON", type=["geojson", "json"])

        if uploaded:

            try:
                data = json.load(uploaded)

                geom = geojson_to_shapely(data)

                st.session_state.field_geom = geom

                for k in default_keys:
                    if k != "field_geom":
                        st.session_state[k] = None

                st.success("Importado!")
                st.rerun()

            except Exception as e:
                st.error(e)

# =========================
# STATS + EXPORT BASE
# =========================

if st.session_state.get("field_geom"):

    st.divider()

    stats = compute_field_stats(st.session_state.field_geom)

    st.metric("Área (ha)", f"{stats['area_ha']:.2f}")
    st.metric("Perímetro (m)", f"{stats['perimeter_m']:.2f}")

    geojson_str = export_geojson([
        {"geometry_wgs84": st.session_state.field_geom}
    ])

    st.download_button(
        "⬇️ GeoJSON",
        geojson_str,
        file_name="talhao.geojson",
        mime="application/json"
    )

# =========================
# TAB 2 - BUFFER
# =========================

with tabs[1]:

    st.header("Buffer")

    if st.session_state.field_geom:

        dist = st.number_input("Distância (m)", 1, 500, 30)

        if st.button("Gerar Buffer"):

            buf = generate_buffer(st.session_state.field_geom, dist)
            st.session_state.buffer_geom = buf
            st.success("Buffer criado!")
            st.rerun()

    else:
        st.info("Crie um talhão primeiro")

# =========================
# TAB 3 - EXPORT
# =========================

with tabs[2]:

    st.header("Exportações")

    if st.session_state.field_geom:

        if st.button("KML"):
            path = export_kml([{"geometry": st.session_state.field_geom}])
            with open(path, "rb") as f:
                st.download_button("Baixar KML", f, file_name="talhao.kml")

        if st.button("Shapefile"):
            path = export_shapefile([{"geometry": st.session_state.field_geom}])
            with open(path, "rb") as f:
                st.download_button("Baixar SHP", f, file_name="talhao.zip")
                