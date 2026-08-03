import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 🔐 VERIFICAÇÃO DE LOGIN
if "token" not in st.session_state or not st.session_state.token:
    st.error("Você precisa fazer login para acessar esta página.")
    st.stop()

# ================== UI ==================
st.title("📊 Dashboard AgroForce")
st.markdown("---")

talhoes = st.session_state.get("talhoes", [])

if not talhoes:
    st.info("Nenhum talhão cadastrado ainda. Vá para **🗺️ Talhões** para começar.")
else:
    # ── MÉTRICAS RÁPIDAS ──────────────────────────────
    total_ha = sum(t['stats']['area_ha'] for t in talhoes)
    com_ndvi = sum(1 for t in talhoes if t.get('grid_cells'))
    com_vra = sum(1 for t in talhoes if t.get('vra_cells'))
    com_buffer = sum(1 for t in talhoes if t.get('buffer_geom'))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🌾 Talhões", len(talhoes))
    col2.metric("📐 Área Total", f"{total_ha:.2f} ha")
    col3.metric("🌿 Com NDVI", com_ndvi)
    col4.metric("🎯 Com VRA", com_vra)
