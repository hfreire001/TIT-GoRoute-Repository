import streamlit as st

# Importamos las vistas principales
from presentacion import login_view, home_view, profile_view, map_view, register_view, search_view
# Importamos el chat desde su subcarpeta
from presentacion.vistas import chat_view

st.set_page_config(page_title="Plan&Go", layout="wide", page_icon="📍")

def main():
    # 🚀 Opciones del menú
    opciones_menu = ["🏠 Feed", "🔍 Explorar", "📍 Crear ruta", "💬 Chat", "👤 Perfil"]

    # 1. Inicialización de sesión
    if 'usuario_logueado' not in st.session_state:
        st.session_state['usuario_logueado'] = None
        
    if 'pagina_actual' not in st.session_state:
        st.session_state['pagina_actual'] = "🏠 Feed"
        
    if 'pantalla_actual' not in st.session_state:
        st.session_state['pantalla_actual'] = "Login"
        
    # Variable para saber qué perfil visualizar (None = el mío propio)
    if 'perfil_a_ver' not in st.session_state:
        st.session_state['perfil_a_ver'] = None

    # 2. Variables del Mapa
    if 'ruta_activa_id' not in st.session_state:
        st.session_state['ruta_activa_id'] = None
    if 'modo_mapa' not in st.session_state:
        st.session_state['modo_mapa'] = 'crear'

    # 3. Lógica de Navegación Inicial (No logueado)
    if st.session_state['usuario_logueado'] is None:
        if st.session_state['pantalla_actual'] == "Login":
            login_view.render() 
        elif st.session_state['pantalla_actual'] == "Registrarse":
            register_view.render()
    else:
        # Lógica de Navegación (Logueado)
        try:
            indice_actual = opciones_menu.index(st.session_state['pagina_actual'])
        except ValueError:
            indice_actual = 0

        # Menú Lateral
        with st.sidebar:
            usuario = st.session_state['usuario_logueado']
            nombre = usuario.get('username', usuario.get('nombre', 'Usuario'))
            st.write(f"Hola, **{nombre}**")
            st.divider()
            
            # El radio button controla la navegación principal
            opcion = st.radio("Ir a:", opciones_menu, index=indice_actual)
            
            # Si el usuario cambia manualmente la opción en el sidebar a algo que NO sea Perfil, 
            # limpiamos el 'perfil_a_ver' para evitar comportamientos extraños
            if opcion != st.session_state['pagina_actual']:
                st.session_state['pagina_actual'] = opcion
                if opcion != "👤 Perfil":
                    st.session_state['perfil_a_ver'] = None
                st.rerun()
            
            st.divider()
            if st.button("Cerrar Sesión"):
                st.session_state['usuario_logueado'] = None
                st.session_state['pagina_actual'] = "🏠 Feed" 
                st.session_state['pantalla_actual'] = "Login"
                st.session_state['perfil_a_ver'] = None
                st.rerun()
                
        # 4. Renderizado de la vista seleccionada
        if st.session_state['pagina_actual'] == "🏠 Feed":
            # Al entrar al Feed, nos aseguramos de limpiar la selección de perfiles ajenos
            st.session_state['perfil_a_ver'] = None
            home_view.render()
            
        elif st.session_state['pagina_actual'] == "🔍 Explorar":
            search_view.render_search()
            
        elif st.session_state['pagina_actual'] == "📍 Crear ruta":
            map_view.render()
            
        elif st.session_state['pagina_actual'] == "💬 Chat":
            chat_view.render_chat_view()
            
        elif st.session_state['pagina_actual'] == "👤 Perfil":
            # LÓGICA CLAVE: 
            # Si perfil_a_ver tiene un ID, renderiza ese perfil.
            # Si es None, renderiza el perfil del usuario logueado.                           
            profile_view.render_profile(st.session_state['usuario_logueado']['id'])

if __name__ == "__main__":
    main()