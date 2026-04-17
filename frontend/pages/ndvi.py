import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import mapping

from utils.ndvi import generate_grid, add_ndvi_to_cells


# ================= STATE =================

def talhao_ativo():
    return st.session_state.get("talhao")


def atualizar_talhao_ativo(chave, valor):
    if "talhao" not in st.session_state:
        st.session_state["talhao"] = {}
    st.session_state["talhao"][chave] = valor


# ================= UI =================

st.header("📊 NDVI / Grade")

ta = talhao_ativo()

if not ta or not ta.get("geom"):
    st.warning("Crie um talhão primeiro.")
else:
    st.caption(f"Talhão: **{ta['nome']}**")

    col_ctrl, col_map = st.columns([1, 3])

    # ================= CONTROLES =================
    with col_ctrl:
        st.subheader("Configuração")

        cell_size = st.number_input(
            "Tamanho da célula (graus ~ ajustar depois)",
            0.0001, 0.01, 0.001
        )

        if st.button("🧩 Gerar Grade", use_container_width=True):
            cells = generate_grid(ta["geom"], cell_size)
            atualizar_talhao_ativo("grid_cells", cells)
            st.success(f"{len(cells)} células geradas")
            st.rerun()

        if ta.get("grid_cells"):
            if st.button("🌿 Calcular NDVI", use_container_width=True):
                cells = add_ndvi_to_cells(ta["grid_cells"])
                atualizar_talhao_ativo("grid_cells", cells)
                st.success("NDVI calculado!")
                st.rerun()

    # ================= MAPA =================
    with col_map:
        c = ta["geom"].centroid

        m = folium.Map(location=[c.y, c.x], zoom_start=14)

        # satélite
        folium.TileLayer(
            'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri'
        ).add_to(m)

        # grid NDVI
        if ta.get("grid_cells"):
            def ndvi_color(v):
                # vermelho → amarelo → verde
                r = int((1 - v) * 255)
                g = int(v * 255)
                return f'#{r:02x}{g:02x}00'

            for cell in ta["grid_cells"][:2000]:
                ndvi = cell.get("ndvi", 0)

                folium.GeoJson(
                    mapping(cell["geometry_wgs84"]),
                    style_function=lambda x, v=ndvi: {
                        "fillColor": ndvi_color(v),
                        "color": "#333",
                        "weight": 0.3,
                        "fillOpacity": 0.7
                    },
                    tooltip=f"NDVI: {ndvi}"
                ).add_to(m)

        # talhão
        folium.GeoJson(
            mapping(ta["geom"]),
            style_function=lambda x: {
                "fillColor": "none",
                "color": "#fff",
                "weight": 3
            }
        ).add_to(m)

        st_folium(m, width=750, height=550)