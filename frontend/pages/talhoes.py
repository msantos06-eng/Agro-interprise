import streamlit as st
import requests
import folium
import json
import pandas as pd

import streamlit as st

def get_headers():
    return {
        "Authorization": f"Bearer {st.session_state.get('token')}"
    }
API = "https://agroforce-production.up.railway.app"

# ... resto do código ...

r = requests.get(
    f"{API}/check-access",
    headers=get_headers()
)


from streamlit_folium import st_folium
from shapely.geometry import mapping
from folium.plugins import Draw, MeasureControl, LocateControl, Geocoder

from utils.geo_utils import geojson_to_shapely, compute_field_stats


# ---------------- ESTADO ----------------
if "talhoes" not in st.session_state:
    st.session_state.talhoes = []
    st.session_state.idx_ativo = 0


st.header("🗺️ Gerenciar Talhões")


col_map, col_ctrl = st.columns([3, 1])


# ================= MAPA =================
with col_map:

    if st.session_state.talhoes:
        pts = [t['geom'].centroid for t in st.session_state.talhoes]
        clat = sum(p.y for p in pts) / len(pts)
        clon = sum(p.x for p in pts) / len(pts)
        zoom_ini = 13
    else:
        clat, clon, zoom_ini = -15.0, -52.0, 5

    m = folium.Map(location=[clat, clon], zoom_start=zoom_ini,
                   max_zoom=22, prefer_canvas=True)

    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satélite',
        max_zoom=22
    ).add_to(m)

    folium.TileLayer('OpenStreetMap', name='Mapa').add_to(m)

    MeasureControl(primary_length_unit='meters',
                   primary_area_unit='hectares').add_to(m)

    LocateControl().add_to(m)
    Geocoder(position='topright').add_to(m)

    # mostrar talhões
    cores = ['#27ae60', '#2980b9', '#e67e22', '#8e44ad']

    for i, t in enumerate(st.session_state.talhoes):
        cor = cores[i % len(cores)]
        ativo = (i == st.session_state.idx_ativo)

        folium.GeoJson(
            mapping(t['geom']),
            name=t['nome'],
            style_function=lambda x, c=cor, a=ativo: {
                'fillColor': c,
                'color': c,
                'weight': 4 if a else 2,
                'fillOpacity': 0.35 if a else 0.2,
            },
            tooltip=f"{t['nome']} -- {t['stats']['area_ha']} ha",
        ).add_to(m)

    Draw(
        draw_options={
            'polygon': True,
            'rectangle': True,
            'polyline': False,
            'circle': False,
            'marker': False,
        }
    ).add_to(m)

    folium.LayerControl().add_to(m)

    out = st_folium(m, width=800, height=550)


# ================= CONTROLE =================
with col_ctrl:

    st.subheader("Novo talhão")

    nome_novo = st.text_input(
        "Nome",
        value=f"Talhão {len(st.session_state.talhoes) + 1}"
    )

    # 🔐 VALIDAÇÃO DE PLANO (AQUI DENTRO)
    r = requests.get(
        f"{API}/check-access",
        headers=get_headers()
    )
st.write(r.status_code, r.json())
  data = r.json()

    if not data.get("allowed"):
    st.error("Limite do plano atingido ou trial expirado.")
    st.stop()

    # 👇 AGORA SIM O BOTÃO
    if st.button("💾 Salvar desenho", use_container_width=True):
        drawings = (out or {}).get('all_drawings') or []

    if drawings:
            try:
                geom = geojson_to_shapely(drawings[-1])
                stats = compute_field_stats(geom)

                novo = {
                    'id': len(st.session_state.talhoes) + 1,
                    'nome': nome_novo,
                    'geom': geom,
                    'stats': stats,
                    'grid_cells': None,
                    'vra_cells': None,
                    'lines': None,
                    'buffer_geom': None,
                }

                st.session_state.talhoes.append(novo)
                st.session_state.idx_ativo = len(st.session_state.talhoes) - 1

                st.success(f"{novo['nome']} salvo ({stats['area_ha']} ha)")
                st.rerun()

            except Exception as e:
                st.error(f"Erro: {e}")
    else:
            st.warning("Desenhe no mapa primeiro.")

    st.divider()

    # IMPORTAÇÃO
    uploaded = st.file_uploader("Importar GeoJSON", type=['geojson', 'json'])

    if uploaded:
        try:
            data = json.load(uploaded)

            features = data.get('features', [data])

            for f in features:
                geom = geojson_to_shapely(f)
                stats = compute_field_stats(geom)

                st.session_state.talhoes.append({
                    'id': len(st.session_state.talhoes) + 1,
                    'nome': f"Importado {len(st.session_state.talhoes)+1}",
                    'geom': geom,
                    'stats': stats,
                    'grid_cells': None,
                    'vra_cells': None,
                    'lines': None,
                    'buffer_geom': None,
                })

            st.success("Importado com sucesso!")
            st.rerun()

        except Exception as e:
            st.error(f"Erro: {e}")

    st.divider()

    # RESUMO
    if st.session_state.talhoes:
        df = pd.DataFrame([
            {
                'Nome': t['nome'],
                'Área (ha)': t['stats']['area_ha']
            }
            for t in st.session_state.talhoes
        ])

        st.dataframe(df, use_container_width=True, hide_index=True)

        total = df['Área (ha)'].sum()
        st.metric("Área total", f"{total:.2f} ha")