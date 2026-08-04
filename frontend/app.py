import base64
import io
from PIL import Image
import streamlit as st
import requests

# Imagens do ConexCrop embutidas em base64 (sem depender de upload de arquivo)
# Gerado automaticamente — não editar a mão

LOGO_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AADTaklEQVR42uy9d5wdZXrn+3uet6pO7KhWRiAEiAGJ2CLOEDQBJmFmvJZsb7K9d735...[SEU_BASE64_LOGO_AQUI]..."
)

WORDMARK_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAyAAAAEiCAYAAAABJ7ZKAAEAAElEQVR42uy9d5wdZXrn+3uet6pO7KhWRiAEiAGJ2CLOEDQBJmFmvJZsb7K9d735...[SEU_BASE64_WORDMARK_AQUI]..."
)

LOGO_IMG = Image.open(io.BytesIO(base64.b64decode(LOGO_PNG_B64)))          # ícone sozinho (favicon)
WORDMARK_IMG = Image.open(io.BytesIO(base64.b64decode(WORDMARK_PNG_B64)))  # ícone + "CONEXCROP"

# ⚙️ CONFIG (SEMPRE PRIMEIRO)
st.set_page_config(
    page_title="ConexCrop",
    layout="wide",
    page_icon=LOGO_IMG,  # ícone da aba do navegador
)

# 🔗 API
API = "https://agro-interprise-production.up.railway.app"

# 🔐 SESSION INIT
if "token" not in st.session_state:
    st.session_state.token = None


# 🔐 HEADERS
def get_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }


# 🖼️ CABEÇALHO (logo + nome já prontos em uma única imagem)
def header():
    st.image(WORDMARK_IMG, width=320)


# 📺 LOGIN / CADASTRO
def tela_login():
    header()
    aba = st.radio("Escolha", ["Login", "Cadastro"])
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if aba == "Login":
        if st.button("Entrar"):
            r = requests.post(
                f"{API}/login",
                json={"email": email, "password": senha}
            )
            if r.status_code == 200:
                st.session_state.token = r.json()["token"]
                st.success("Login realizado!")
                st.rerun()
            else:
                st.error("Login inválido")
    if aba == "Cadastro":
        if st.button("Cadastrar"):
            r = requests.post(
                f"{API}/register",
                json={"email": email, "password": senha}
            )
            if r.status_code == 200:
                st.session_state.token = r.json()["token"]
                st.success("Conta criada!")
                st.rerun()
            else:
                st.error("Erro ao cadastrar")
                st.write("STATUS:", r.status_code)
                st.write("RESPOSTA:", r.text)


# 📊 dados usuário
def get_user_data():
    try:
        r = requests.get(f"{API}/me", headers=get_headers())
        if r.status_code == 200:
            return r.json()
        else:
            st.error(f"Erro ao carregar usuário: {r.status_code}")
            st.session_state.token = None
            st.rerun()
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        st.session_state.token = None
        st.rerun()


# 📊 DASHBOARD
def dashboard():
    header()

    user_data = get_user_data()
    if not user_data:
        st.stop()

    # 📊 SIDEBAR
    st.sidebar.image(WORDMARK_IMG, width=180)
    st.sidebar.title("Conta")
    plano = user_data.get("plan", "free")
    if plano == "free":
        st.sidebar.warning("Plano FREE")
    else:
        st.sidebar.success(f"Plano {plano.upper()}")

    # 🚀 upgrade
    if plano == "free":
        if st.sidebar.button("🚀 Fazer Upgrade"):
            r = requests.get(
                f"{API}/create-payment-link",
                headers=get_headers()
            )
            if r.status_code == 200:
                link = r.json().get("url")
                if link:
                    st.sidebar.markdown(f"[💳 Pagar agora]({link})")
            else:
                st.error("Erro ao gerar pagamento")

    # 🔓 logout
    if st.sidebar.button("Sair"):
        st.session_state.token = None
        st.rerun()

    st.markdown("### Bem-vindo! 👋")
    st.info("Use o menu lateral para acessar Talhões, Buffer, NDVI, Taxa Variável, Projeção de Linha e Exportar.")


# 🔥 CONTROLE CENTRAL — navegação condicional
# As páginas de funcionalidades só existem na lista (e portanto só aparecem
# no menu lateral) quando o usuário está logado.
page_login = st.Page(tela_login, title="Login", icon="🔐", url_path="login")
page_inicio = st.Page(dashboard, title="Início", icon="🏠", default=True, url_path="inicio")
page_projetos = st.Page("pages/projetos.py", title="Projetos", icon="📁", url_path="projetos")
page_dashboard_file = st.Page("pages/dashboard.py", title="Dashboard", icon="📈", url_path="dashboard-analitico")
page_talhoes = st.Page("pages/talhoes.py", title="Talhões", icon="🗺️", url_path="talhoes")
page_buffer = st.Page("pages/buffer.py", title="Buffer", icon="🔵", url_path="buffer")
page_ndvi = st.Page("pages/ndvi.py", title="NDVI / Grade", icon="📊", url_path="ndvi")
page_vra = st.Page("pages/vra.py", title="Taxa Variável (VRA)", icon="🎯", url_path="vra")
page_linhas = st.Page("pages/linhas.py", title="Projeção de Linha", icon="🌾", url_path="linhas")
page_exportar = st.Page("pages/exportar.py", title="Exportar", icon="📤", url_path="exportar")

if st.session_state.token:
    pg = st.navigation([
        page_inicio,
        page_projetos,
        page_dashboard_file,
        page_talhoes,
        page_buffer,
        page_ndvi,
        page_vra,
        page_linhas,
        page_exportar,
    ])
else:
    pg = st.navigation([page_login])

pg.run()
