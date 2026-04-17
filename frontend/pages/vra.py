import numpy as np
import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import mapping

from utils.geo_utils import generate_buffer
from utils.export_utils import export_geojson


def talhao_ativo():
    return st.session_state.get("talhao")


def atualizar_talhao_ativo(chave, valor):
    if "talhao" not in st.session_state:
        st.session_state["talhao"] = {}
    st.session_state["talhao"][chave] = valor


def add_vra_to_cells(cells, produto, dose_min, dose_max, modo):
    ndvis = [c.get("ndvi", 0) for c in cells]

    mn = min(ndvis)
    mx = max(ndvis)
    rng = mx - mn if mx != mn else 1

    for c in cells:
        ndvi = c.get("ndvi", 0)
        t = (ndvi - mn) / rng

        if modo == "inversa":
            t = 1 - t

        dose = dose_min + t * (dose_max - dose_min)

        c["dose"] = round(dose, 2)
        c["produto"] = produto

    return cells


# ================== UI ==================

st.header("🎯 Taxa Variável (VRA)")

ta = talhao_ativo()

if not ta or not ta.get('grid_cells'):
    st.info("Gere a grade NDVI primeiro (aba **NDVI / Grade**).")
else:
    st.caption(f"Talhão ativo: **{ta['nome']}** -- {ta['stats']['area_ha']} ha")

    col_ctrl, col_map = st.columns([1, 3])

    with col_ctrl:
        st.subheader("Configuração")
        produto = st.text_input("Produto", "Ureia")
        unidade = st.selectbox("Unidade", ['kg/ha', 'L/ha', 'ton/ha'])
        dose_min = st.number_input("Dose mínima", 0.0, 9999.0, 50.0, step=10.0)
        dose_max = st.number_input("Dose máxima", 0.0, 9999.0, 150.0, step=10.0)

        relacao = st.radio(
            "Relação com NDVI",
            ['Inversa -- baixo NDVI → mais dose',
             'Direta -- alto NDVI → mais dose']
        )

        if st.button("🎯 Calcular VRA", type="primary", use_container_width=True):
            try:
                modo = 'inversa' if 'Inversa' in relacao else 'direta'

                cells = add_vra_to_cells(
                    [dict(c) for c in ta['grid_cells']],
                    produto, dose_min, dose_max, modo
                )

                atualizar_talhao_ativo('vra_cells', cells)

                total_area = sum(c['area_ha'] for c in cells)
                total_dose = sum(c['dose'] * c['area_ha'] for c in cells)

                st.success("VRA calculado!")
                st.metric("Dose média", f"{total_dose/total_area:.1f} {unidade}")
                st.metric("Total produto", f"{total_dose:.0f} kg")

                st.rerun()

            except Exception as e:
                st.error(f"Erro: {e}")

        if ta.get('vra_cells'):
            doses = [c['dose'] for c in ta['vra_cells']]

            st.divider()
            st.metric("Dose média", f"{np.mean(doses):.1f} {unidade}")
            st.metric("Dose máx", f"{np.max(doses):.1f}")
            st.metric("Dose mín", f"{np.min(doses):.1f}")

            geojson_str = export_geojson(
                ta['vra_cells'],
                properties=['cell_id', 'area_ha', 'ndvi', 'dose', 'produto']
            )

            st.download_button(
                "⬇️ Baixar VRA GeoJSON",
                geojson_str,
                file_name=f"vra_{ta['nome']}.geojson",
                mime="application/json",
                use_container_width=True
            )

    with col_map:
        c = ta['geom'].centroid

        m = folium.Map(location=[c.y, c.x], zoom_start=14, max_zoom=22)

        folium.TileLayer(
            'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Satélite',
            max_zoom=22
        ).add_to(m)

        if ta.get('vra_cells'):
            all_doses = [c['dose'] for c in ta['vra_cells']]
            mn, mx = min(all_doses), max(all_doses)
            rng = mx - mn if mx != mn else 1

            def dose_color(d):
                t = (d - mn) / rng
                r = int(t * 220)
                g = int((1 - abs(2 * t - 1)) * 160)
                b = int((1 - t) * 220)
                return f'#{r:02x}{g:02x}{b:02x}'

            for cell in ta['vra_cells'][:2000]:
                color = dose_color(cell['dose'])

                folium.GeoJson(
                    mapping(cell['geometry_wgs84']),
                    style_function=lambda x, c=color: {
                        'fillColor': c,
                        'color': '#333',
                        'weight': 0.5,
                        'fillOpacity': 0.85
                    },
                    tooltip=f"{cell.get('produto','')} {cell['dose']} {unidade}"
                ).add_to(m)

        folium.GeoJson(
            mapping(ta['geom']),
            style_function=lambda x: {
                'fillColor': 'none',
                'color': '#fff',
                'weight': 3
            }
        ).add_to(m)

        st_folium(m, width=760, height=550, key='map_vra')