import streamlit as st
from services.api import login

def show_login():
    st.title("Login")

    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        res = login(email, password)

        if "access_token" in res:
            st.session_state["token"] = res["access_token"]
            st.success("Login OK")
        else:
            st.error("Erro no login")