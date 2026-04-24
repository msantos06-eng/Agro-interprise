import streamlit as st

import streamlit as st

if not st.session_state.get("token"):
    st.warning("Faça login primeiro")
    st.stop()

st.title("Dashboard")

def show_dashboard():
    st.title("Dashboard Agro Saas")
    st.write("Bem-vindo ao sistema")