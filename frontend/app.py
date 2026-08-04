import base64
import io
import pandas as pd
import numpy as np
from PIL import Image
import streamlit as st

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="ConexCrop",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. LOGO EM BASE64 & FUNÇÃO DE CARREGAMENTO
# ---------------------------------------------------------
LOGO_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AADTaklEQVR42uy9d5wdZXrn+3uet6pO7KhWRiAEiAGJ2CLOEDQBJmFmvJZsb7K9d717r733brC93uskcNpwPV57s8PaXu96bUueGcIMM8AM0sAAAiSiBIwEAkkodavT6ROr6n2f+0fVOX06qFtCEen58imO"
    "uvucqjpVb71PeJ8AKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqi"
    "KIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqi"
    "KIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqi"
    "KIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqi"
    "KIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqi"
    "KIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIqiKIpy7iEiJCKkV0JRFEVRFEVRFEVRzler/8CBA3kR6RWRLhHJiQjr1VGUE8PTS6CcC5P66dgvEcnZPL9TdXxl0jUFAKmM1/4PAL9Yr8X7iWWTtdFGAB+ICOl1V5TjfJ70EihnQzgD"
    "wKXNm/hHf/RHrcjpma+JCH/9139t1q1bJ5s2bZr2PdatW+dOpxBvO747Bd9FdCxKFoA3MDCABQsW5IcwVH9q07zKunXIAIiJKNQndtK1al6PgIjqelUUVQCU42Ljxo3mdArnKZNV59tvvy1jYyYdj8Po7b0cvb0ntp933nkHANDV1SUf+9jHiIhKp+r8jh49KkREwwCG"
    "0+OgtxcYnv7+ri57So/frkysX7/eXoDCzCeiqFof+7mMX/i3tXp53PczZNg8ZYz/74nombOtJJ8rCpqIeEQUlyq1f0wu+xBwBMLZL3UWuv+g+Ted3RRVAJTjmtCOHk2Es+eNtcbKLbfcckL7Gxoawosvvtj6OZfLMQB0dHTfXCx2/Avr3C21Wh1EYEBgrcPii5ZiwYL5"
    "iMJG0+0787m2/fvdd95FuVqBZ4zL5XLwvOCF0vDgv41jGvd9s0gksYhERMRI1oXh9o9//OPlY+yaAXjlevgn2SC4qx42nDGGK9Uq3nv33aZUBhHPcP3I5bIZsDEvjI+P/m5m3rwXr1++HACO2xOwe/duvPPOOwjDUK6++mpauXJlqXlvNm3axBeSIpB6oWhkZKQjm/P+"
    "0vcydzfCqhTy3XkAqDfKr4DMlmyQ+9VNmzbV161bx9u3bz+ufff3n9i5TOx2O4B+rFmzJmoK3u3bt9Oxj9Pf9rlZzwjAdrSffn9/v9u0adO0d65bt46ax+zv758k2PcD2WVACGzCftwaLMOyunqTFFUAlFkn2i1btphPfvKT8c6dO+9hE/yL2Lpb6rUaALC1FoVCAcuW"
    "XQRrHowAEKw6SfLZlqbbtD77nYbxUwvDICDzPh4gDBAQSMcbrzGeyqFQqgGGICIgIzjp093Sju6cHURSC24RsyyNBAIGS9zsHYwwOHT6MsNEAM8M5h0KhiHK5DGet9TzfOOcAEQgBTAxrbXXx0sUxM7f2O8XjwR3FYrHRSJUQIkRhiIGBgUTxEJn6/tb3d86hWCyiUqmg"
    "kM+Xenp6KLJWpuoyJl1hSfY/8Z1GR0cxOjYKR+QC3wcgL8T1xr+/vprHj/XrM4zrJSSiGRHRvYEfrbvH4qz2YzvdzgA2aD4K2fDwt21a1dnU0H7KLB582bv7vrvtqoIKKoAXOACv13Y7d6921u5cmXjuee3PdTT030/GYMojuF7PjzPgzGmJayYE6FsnZ2kAMxwDDBz"
    "67PNVwCI4xhinU2tbTTPRlLBau2xjdx2RaP5b2ZunVeKA9gQEay1Mmm8i4gxhmQWozw9B9f+OWICIfn+yXlOfoqICBCgqQcAMCICYwycc9MVhtZ7J3bS/h2EBLGNEfgZOBvDRvG3G7Xa71111RRPbf311E1sp"
)

@st.cache_data
def load_logo(b64_str: str) -> Image.Image:
    """Decodifica a string base64 e retorna o objeto de imagem PIL."""
    try:
        img_bytes = base64.b64decode(b64_str)
        return Image.open(io.BytesIO(img_bytes))
    except Exception:
        return None

# ---------------------------------------------------------
# 3. MOCK DATA (Geração de Dados de Exemplo)
# ---------------------------------------------------------
@st.cache_data
def get_crop_data():
    dates = pd.date_range(start="2026-07-01", periods=35, freq="D")
    data = {
        "Data": dates,
        "Umidade Solo (%)": np.random.uniform(45, 85, size=35).round(1),
        "Temperatura (°C)": np.random.uniform(22, 36, size=35).round(1),
        "Produtividade Est. (ton)": np.random.uniform(12, 28, size=35).round(1),
        "Cultura": np.random.choice(["Soja", "Milho", "Algodão"], size=35)
    }
    return pd.DataFrame(data)

df = get_crop_data()

# ---------------------------------------------------------
# 4. BARRA LATERAL (SIDEBAR)
# ---------------------------------------------------------
with st.sidebar:
    # Exibe a logo
    logo_img = load_logo(LOGO_PNG_B64)
    if logo_img:
        st.image(logo_img, use_container_width=True)
    else:
        st.title("🌱 ConexCrop")

    st.markdown("---")
    st.header("⚙️ Painel de Controle")

    # Módulo de Navegação
    modulo = st.radio(
        "Navegação:",
        ["Visão Geral", "Monitoramento de Solo", "Relatório de Produção"],
        index=0
    )

    st.markdown("---")
    st.subheader("Filtros")

    # Filtro por Cultura
    culturas = df["Cultura"].unique().tolist()
    cultura_sel = st.multiselect(
        "Culturas:",
        options=culturas,
        default=culturas
    )

    # Filtro de Intervalo de Dias
    dias_filtro = st.slider("Últimos dias:", min_value=7, max_value=35, value=30)

# Filtragem dos dados conforme seleção da Sidebar
df_filtrado = df[df["Cultura"].isin(cultura_sel)].tail(dias_filtro)

# ---------------------------------------------------------
# 5. ÁREA PRINCIPAL
# ---------------------------------------------------------
st.title("🚜 ConexCrop - Gestão Inteligente de Lavouras")

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
else:
    # MÓDULO 1: VISÃO GERAL
    if modulo == "Visão Geral":
        st.subheader("📊 Indicadores Principais (KPIs)")

        col1, col2, col3, col4 = st.columns(4)
        
        media_umidade = df_filtrado["Umidade Solo (%)"].mean()
        media_temp = df_filtrado["Temperatura (°C)"].mean()
        total_prod = df_filtrado["Produtividade Est. (ton)"].sum()

        col1.metric("Umidade Média", f"{media_umidade:.1f}%", "+2.4%")
        col2.metric("Temperatura Média", f"{media_temp:.1f} °C", "-0.5 °C")
        col3.metric("Produtividade Est.", f"{total_prod:.1f} ton", "+4.1%")
        col4.metric("Área Monitorada", "1.450 ha", "Estável")

        st.markdown("---")

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.markdown("### 📈 Umidade do Solo por Dia")
            st.line_chart(df_filtrado.set_index("Data")["Umidade Solo (%)"])

        with col_g2:
            st.markdown("### 📊 Estimativa por Cultura (ton)")
            prod_cultura = df_filtrado.groupby("Cultura")["Produtividade Est. (ton)"].sum()
            st.bar_chart(prod_cultura)

    # MÓDULO 2: MONITORAMENTO DE SOLO
    elif modulo == "Monitoramento de Solo":
        st.subheader("🌡️ Monitoramento Ambiental em Tempo Real")

        st.markdown("##### Umidade (%) vs Temperatura (°C)")
        st.line_chart(
            df_filtrado.set_index("Data")[["Umidade Solo (%)", "Temperatura (°C)"]]
        )

        with st.expander("📄 Ver Tabela do Período"):
            st.dataframe(df_filtrado, use_container_width=True)

    # MÓDULO 3: RELATÓRIO DE PRODUÇÃO
    elif modulo == "Relatório de Produção":
        st.subheader("📋 Resumo de Produção por Cultura")

        resumo = df_filtrado.groupby("Cultura").agg(
            Umidade_Media=("Umidade Solo (%)", "mean"),
            Temp_Media=("Temperatura (°C)", "mean"),
            Produtividade_Total=("Produtividade Est. (ton)", "sum")
        ).reset_index()

        st.dataframe(resumo, use_container_width=True)

        st.download_button(
            label="📥 Baixar Dados em CSV",
            data=df_filtrado.to_csv(index=False).encode("utf-8"),
            file_name="conexcrop_relatorio.csv",
            mime="text/csv"
        )
