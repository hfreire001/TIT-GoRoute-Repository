import streamlit as st

# Importamos las dos vistas de la capa de presentación
from presentacion import login_view 
from presentacion import home_view

st.set_page_config(page_title="Plan&Go", layout="wide", page_icon="📍")

def main():
    # 1. Inicializamos la memoria de la sesión si no existe
    if 'usuario_logueado' not in st.session_state:
        st.session_state['usuario_logueado'] = None
        
    # Variables de navegación del mapa para que no exploten los botones
    if 'ruta_activa_id' not in st.session_state:
        st.session_state['ruta_activa_id'] = None
    if 'modo_mapa' not in st.session_state:
        st.session_state['modo_mapa'] = 'crear'

    # 2. EL PORTERO DE LA DISCOTECA (Control de acceso)
    if st.session_state['usuario_logueado'] is None:
        # Si NO hay usuario, renderizamos la pantalla de Login
        # (Asumo que tu login_view tiene una función llamada render() o main())
        login_view.render() 
    else:
        # Si SÍ ha iniciado sesión, mostramos el Feed
        with st.sidebar:
            st.write(f"Hola, **{st.session_state['usuario_logueado']['username']}**")
            if st.button("Cerrar Sesión"):
                st.session_state['usuario_logueado'] = None
                st.rerun()
                
        # Cargamos el feed principal
        home_view.render()

if __name__ == "__main__":
    main()