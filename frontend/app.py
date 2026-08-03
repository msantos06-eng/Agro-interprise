import base64
import streamlit as st
import requests


def _logo_base64():
    with open("assets/logo.png", "rb") as f:
        return base64.b64encode(f.read()).decode()

# ⚙️ CONFIG (SEMPRE PRIMEIRO)
st.set_page_config(
    page_title="ConexCrop",
    layout="wide",
    page_icon="assets/logo.png",  # ícone da aba do navegador
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


# 🖼️ CABEÇALHO COM LOGO (colada ao nome, mesma linha)
def header():
    logo_b64 = _logo_base64()
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:0.5rem;">
            <img src="data:image/png;base64,{logo_b64}" style="height:48px;">
            <span style="font-size:2.2rem; font-weight:700; line-height:1;">ConexCrop</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
    st.sidebar.image("assets/logo.png", width=80)
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

    st.markdown("Selecione uma funcionalidade abaixo")

    # ── Tabs (só aparecem após login/cadastro) ─────────────────
    tabs = st.tabs([
        "🗺️ Talhões",
        "🔵 Buffer",
        "📊 NDVI / Grade",
        "🎯 Taxa Variável",
        "🌾 Proj. de Linha",
        "📤 Exportar",
    ])

    with tabs[0]:
        st.subheader("🗺️ Talhões")
        st.info("Em construção")

    with tabs[1]:
        st.subheader("🔵 Buffer")
        st.info("Em construção")

    with tabs[2]:
        st.subheader("📊 NDVI / Grade")
        st.info("Em construção")

    with tabs[3]:
        st.subheader("🎯 Taxa Variável")
        st.info("Em construção")

    with tabs[4]:
        st.subheader("🌾 Projeção de Linha")
        st.info("Em construção")

    with tabs[5]:
        st.subheader("📤 Exportar")
        st.info("Em construção")


# 🔥 CONTROLE CENTRAL
if not st.session_state.token:
    tela_login()
    st.stop()

dashboard()
