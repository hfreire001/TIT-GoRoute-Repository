import streamlit as st

# Importamos las 4 vistas (asegúrate de que los nombres de archivo sean correctos)
from presentacion import login_view, home_view, profile_view, map_view

st.set_page_config(page_title="Plan&Go", layout="wide", page_icon="📍")

def main():
    # 1. Inicialización de sesión
    if 'usuario_logueado' not in st.session_state:
        st.session_state['usuario_logueado'] = None
        
    # 2. Variables del Mapa (para que no de error al cargar la vista del mapa)
    if 'ruta_activa_id' not in st.session_state:
        st.session_state['ruta_activa_id'] = None
    if 'modo_mapa' not in st.session_state:
        st.session_state['modo_mapa'] = 'crear'

    # 3. Lógica de Navegación
    if st.session_state['usuario_logueado'] is None:
        # Si no hay nadie, al Login
        login_view.render() 
    else:
        # Menú Lateral para el usuario logueado
        with st.sidebar:
            usuario = st.session_state['usuario_logueado']
            nombre = usuario.get('username', usuario.get('nombre', 'Usuario'))
            st.write(f"Hola, **{nombre}**")
            st.divider()
            
            # Selector de página con el nuevo nombre "Crear ruta"
            opcion = st.radio("Ir a:", ["🏠 Feed", "📍 Crear ruta", "👤 Perfil"])
            
            st.divider()
            if st.button("Cerrar Sesión"):
                st.session_state['usuario_logueado'] = None
                st.rerun()
                
        # Renderizado de la vista seleccionada
        if opcion == "🏠 Feed":
            home_view.render()
        elif opcion == "📍 Crear ruta":
            # Aquí llamamos a la vista del mapa
            map_view.render()
        elif opcion == "👤 Perfil":
            id_actual = st.session_state['usuario_logueado']['id']
            profile_view.render_profile(id_actual)

if __name__ == "__main__":
    main()