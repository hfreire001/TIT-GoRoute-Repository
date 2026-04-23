# run_chat.py
import streamlit as st
from presentacion.vistas import chat_view

# 1. Configuración de la página (Debe ser lo primero en ejecutarse)
st.set_page_config(page_title="Plan&Go - Chat", page_icon="💬", layout="wide")

# 2. Panel lateral de pruebas para cambiar de usuario fácilmente
st.sidebar.title("🛠️ Panel de Pruebas")
st.sidebar.write("Simulador de sesión activa:")

usuario_simulado = st.sidebar.selectbox(
    "Iniciar sesión como:",
    options=[1, 2, 3, 4], # Asegúrate de que estos IDs existan en tu tabla 'users'
    format_func=lambda x: f"Usuario ID: {x}"
)

# Guardamos el usuario en la sesión
st.session_state.user_id = usuario_simulado

# 3. Lanzamos la vista principal del chat
chat_view.render_chat_view()