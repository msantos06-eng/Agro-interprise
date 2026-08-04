import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# 🔐 VERIFICAÇÃO DE LOGIN
if "token" not in st.session_state or not st.session_state.token:
    st.error("Você precisa fazer login para acessar esta página.")
    st.stop()
# ================== ESTILO ==================
st.markdown("""
<style>
    .card {
        background-color: #1e2130;
        border-radius: 12px;
        padding: 20px;
        margin: 8px 0;
        border-left: 4px solid #27ae60;
    }
    .card-title {
        color: #aab4c4;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .card-value {
        color: #ffffff;
        font-size: 32px;
        font-weight: bold;
    }
    .card-sub {
        color: #27ae60;
        font-size: 13px;
    }
    .header-bar {
        background: linear-gradient(90deg, #1a6b3c, #2980b9);
        padding: 16px 24px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ================== HEADER ==================
st.markdown("""
<div class="header-bar">
    <h2 style="color:white; margin:0;">🌾 AgroForce — Painel de Controle</h2>
    <p style="color:#cde; margin:0; font-size:13px;">Visão geral da operação agrícola</p>
</div>
""", unsafe_allow_html=True)

talhoes = st.session_state.get("talhoes", [])

if not talhoes:
    st.info("Nenhum talhão cadastrado ainda. Vá para **🗺️ Talhões** para começar.")
    st.stop()

# ================== DADOS ==================
total_ha = sum(t['stats']['area_ha'] for t in talhoes)
com_ndvi = sum(1 for t in talhoes if t.get('grid_cells'))
com_vra = sum(1 for t in talhoes if t.get('vra_cells'))
com_buffer = sum(1 for t in talhoes if t.get('buffer_geom'))
com_linhas = sum(1 for t in talhoes if t.get('lines'))

# ================== FILTRO ==================
nomes = [t['nome'] for t in talhoes]
filtro = st.multiselect("🔍 Filtrar talhões", nomes, default=nomes)
talhoes_filtrados = [t for t in talhoes if t['nome'] in filtro]

if not talhoes_filtrados:
    st.warning("Nenhum talhão selecionado.")
    st.stop()

# ================== KPI CARDS ==================
st.markdown("### 📊 Indicadores")
c1, c2, c3, c4, c5 = st.columns(5)

def card(col, titulo, valor, sub, cor="#27ae60"):
    col.markdown(f"""
    <div class="card" style="border-left-color:{cor};">
        <div class="card-title">{titulo}</div>
        <div class="card-value">{valor}</div>
        <div class="card-sub" style="color:{cor};">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

card(c1, "Talhões", len(talhoes_filtrados), "cadastrados", "#27ae60")
card(c2, "Área Total", f"{sum(t['stats']['area_ha'] for t in talhoes_filtrados):.1f} ha", "em produção", "#2980b9")
card(c3, "Com NDVI", sum(1 for t in talhoes_filtrados if t.get('grid_cells')), "analisados", "#e67e22")
card(c4, "Com VRA", sum(1 for t in talhoes_filtrados if t.get('vra_cells')), "prescrito", "#8e44ad")
card(c5, "Com Buffer", sum(1 for t in talhoes_filtrados if t.get('buffer_geom')), "calculados", "#e74c3c")

st.markdown("---")

# ================== GRÁFICOS ==================
col_bar, col_pie = st.columns([3, 2])

with col_bar:
    st.markdown("### 📐 Área por Talhão")
    fig, ax = plt.subplots(figsize=(7, 3))
    fig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#1e2130')

    nomes_f = [t['nome'] for t in talhoes_filtrados]
    areas_f = [t['stats']['area_ha'] for t in talhoes_filtrados]
    cores = ['#27ae60', '#2980b9', '#e67e22', '#8e44ad', '#e74c3c']

    bars = ax.barh(nomes_f, areas_f,
                   color=[cores[i % len(cores)] for i in range(len(nomes_f))],
                   height=0.5)

    for bar, val in zip(bars, areas_f):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                f'{val:.1f} ha', va='center', color='white', fontsize=10)

    ax.set_xlabel("Hectares", color='#aab4c4')
    ax.tick_params(colors='#aab4c4')
    ax.spines[:].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)

with col_pie:
    st.markdown("### 🔎 Status das Análises")
    fig2, ax2 = plt.subplots(figsize=(4, 4))
    fig2.patch.set_facecolor('#0e1117')
    ax2.set_facecolor('#1e2130')

    categorias = ['NDVI', 'VRA', 'Buffer', 'Linhas']
    valores = [
        sum(1 for t in talhoes_filtrados if t.get('grid_cells')),
        sum(1 for t in talhoes_filtrados if t.get('vra_cells')),
        sum(1 for t in talhoes_filtrados if t.get('buffer_geom')),
        sum(1 for t in talhoes_filtrados if t.get('lines')),
    ]
    cores_bar = ['#27ae60', '#8e44ad', '#e74c3c', '#2980b9']

    ax2.bar(categorias, valores, color=cores_bar, width=0.5)
    ax2.set_ylim(0, max(len(talhoes_filtrados), 1))
    ax2.tick_params(colors='#aab4c4')
    ax2.spines[:].set_visible(False)
    ax2.set_facecolor('#1e2130')
    plt.tight_layout()
    st.pyplot(fig2)

st.markdown("---")

# ================== TABELA ==================
st.markdown("### 📋 Detalhamento dos Talhões")

df = pd.DataFrame([
    {
        'Nome': t['nome'],
        'Área (ha)': t['stats']['area_ha'],
        'NDVI': '✅' if t.get('grid_cells') else '❌',
        'VRA': '✅' if t.get('vra_cells') else '❌',
        'Buffer': '✅' if t.get('buffer_geom') else '❌',
        'Linhas': '✅' if t.get('lines') else '❌',
    }
    for t in talhoes_filtrados
])

st.dataframe(df, use_container_width=True, hide_index=True)

total = sum(t['stats']['area_ha'] for t in talhoes_filtrados)
st.markdown(f"**Área total filtrada: `{total:.2f} ha`**")
