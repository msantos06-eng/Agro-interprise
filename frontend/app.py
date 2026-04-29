import streamlit as st
import requests

# ⚙️ CONFIG (SEMPRE PRIMEIRO)
st.set_page_config(page_title="AgroForce", layout="wide", page_icon="🌾")

# 🔗 API
API = "https://agroforce-production.up.railway.app"

# 🔐 SESSION INIT
if "token" not in st.session_state:
    st.session_state.token = None


# 🔐 HEADERS
def get_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }


# 📺 LOGIN / CADASTRO
def tela_login():
    st.title("🌾 AgroForce")

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


# 📊 DASHBOARD
def dashboard():
    st.title("Dashboard")

    # 📊 dados usuário
    @st.cache_data(ttl=30)
    def get_user_data():
        r = requests.get(f"{API}/me", headers=get_headers())
        return r.json()

    user_data = get_user_data()

    # 📊 SIDEBAR
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

    st.markdown("Selecione uma funcionalidade no menu lateral")


# 🔥 CONTROLE CENTRAL (CORRETO)
if not st.session_state.token:
    tela_login()
    st.stop()

dashboard()


# ── Tabs ─────────────────────────────────────────────
tabs = st.tabs([
    "🗺️ Talhões",
    "🔵 Buffer",
    "📊 NDVI / Grade",
    "🎯 Taxa Variável",
    "🌾 Proj. de Linha",
    "📤 Exportar",
])
