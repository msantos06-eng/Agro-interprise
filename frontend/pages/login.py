import streamlit as st

st.title("Login")

email = st.text_input("Email")
senha = st.text_input("Senha", type="password")

if st.button("Entrar"):
    # chamada API aqui
    st.session_state["token"] = "ok"