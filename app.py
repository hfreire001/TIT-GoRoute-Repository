import streamlit as st

# Importamos las TRES vistas que tenemos hasta ahora
from presentacion import login_view 
from presentacion import home_view
from presentacion import profile_view 

st.set_page_config(page_title="Plan&Go", layout="wide", page_icon="📍")

def main():
    if 'usuario_logueado' not in st.session_state:
        st.session_state['usuario_logueado'] = None
        
    if 'ruta_activa_id' not in st.session_state:
        st.session_state['ruta_activa_id'] = None
    if 'modo_mapa' not in st.session_state:
        st.session_state['modo_mapa'] = 'crear'

    # Control de acceso
    if st.session_state['usuario_logueado'] is None:
        login_view.render() 
    else:
        # Menú Lateral de Navegación
        with st.sidebar:
            st.write(f"Hola, **{st.session_state['usuario_logueado']['username']}**")
            st.divider()
            
            # El usuario elige a dónde ir
            opcion = st.radio("Menú de Navegación", ["🏠 Mi Feed", "👤 Mi Perfil"])
            
            st.divider()
            if st.button("Cerrar Sesión"):
                st.session_state['usuario_logueado'] = None
                st.rerun()
                
        # Cargamos la vista que haya elegido
        if opcion == "🏠 Mi Feed":
            home_view.render()
        id_usuario = st.session_state['usuario_logueado']['id']
        
        # Llamamos a la función del perfil pasándole ese ID
        profile_view.render_profile(id_usuario)

if __name__ == "__main__":
    main()