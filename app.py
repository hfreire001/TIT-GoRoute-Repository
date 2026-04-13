# app.py
import streamlit as st
from presentacion import profile_view

st.set_page_config(page_title="Plan & Go", layout="wide")

# Forzamos el ID 3 para la prueba real con tu tabla 'users'
if "user_id" not in st.session_state:
    st.session_state.user_id = 3 

profile_view.render_profile(st.session_state.user_id)