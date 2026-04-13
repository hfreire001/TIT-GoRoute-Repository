import streamlit as st
from presentacion import home_view

st.set_page_config(page_title="Plan&Go - Test Feed", layout="wide", page_icon="📱")

def main():
    # ==========================================
    # 🚀 MODO PRUEBA: FORZAR USUARIO LOGUEADO
    # ==========================================
    # Si no hay nadie logueado, metemos un usuario a la fuerza
    if 'usuario_logueado' not in st.session_state or st.session_state['usuario_logueado'] is None:
        st.session_state['usuario_logueado'] = {'id': 4, 'nombre': 'Garazi_PlanGo'} # <-- Cambia el 1 o el nombre por el que quieras probar
        
    # Variables de navegación del mapa para que no exploten los botones
    if 'ruta_activa_id' not in st.session_state:
        st.session_state['ruta_activa_id'] = None
    if 'modo_mapa' not in st.session_state:
        st.session_state['modo_mapa'] = 'crear'

    # Saltamos directo al feed
    home_view.render()

if __name__ == "__main__":
    main()