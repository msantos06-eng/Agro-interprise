import streamlit as st

def get_talhoes():
    if "talhoes" not in st.session_state:
        st.session_state.talhoes = []
    return st.session_state.talhoes