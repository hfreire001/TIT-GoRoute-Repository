import streamlit as st

# Importamos las vistas principales
from presentacion import login_view, home_view, profile_view, map_view, register_view, search_view
# Importamos el chat desde su subcarpeta
from presentacion.vistas import chat_view

st.set_page_config(page_title="Plan&Go", layout="wide", page_icon="📍")

def main():
    # Opciones del menú actualizadas con Explorar y Chat
    opciones_menu = ["🏠 Feed", "🔍 Explorar", "📍 Crear ruta", "💬 Chat", "👤 Perfil"]

    # 1. Inicialización de sesión
    if 'usuario_logueado' not in st.session_state:
        st.session_state['usuario_logueado'] = None
        
    if 'pagina_actual' not in st.session_state:
        st.session_state['pagina_actual'] = "🏠 Feed"
        
    if 'pantalla_actual' not in st.session_state:
        st.session_state['pantalla_actual'] = "Login"
        
    # 2. Variables del Mapa
    if 'ruta_activa_id' not in st.session_state:
        st.session_state['ruta_activa_id'] = None
    if 'modo_mapa' not in st.session_state:
        st.session_state['modo_mapa'] = 'crear'

    # 3. Lógica de Navegación Inicial (Login vs Registro)
    if st.session_state['usuario_logueado'] is None:
        if st.session_state['pantalla_actual'] == "Login":
            login_view.render() 
        elif st.session_state['pantalla_actual'] == "Registrarse":
            register_view.render()
    else:
        try:
            indice_actual = opciones_menu.index(st.session_state['pagina_actual'])
        except ValueError:
            indice_actual = 0

        # Menú Lateral para el usuario logueado
        with st.sidebar:
            usuario = st.session_state['usuario_logueado']
            nombre = usuario.get('username', usuario.get('nombre', 'Usuario'))
            st.write(f"Hola, **{nombre}**")
            st.divider()
            
            opcion = st.radio("Ir a:", opciones_menu, index=indice_actual)
            
            # 🚀 AQUÍ SEPARAMOS ESTRICTAMENTE LOS MÓDULOS AL NAVEGAR
            if opcion != st.session_state['pagina_actual']:
                st.session_state['pagina_actual'] = opcion
                
                if opcion == "📍 Crear ruta":
                    # Entrar a crear ruta SIEMPRE es desde 0
                    st.session_state['modo_mapa'] = 'crear'
                    st.session_state['ruta_activa_id'] = None
                    st.session_state['editando_route_id'] = None
                    st.session_state['puntos_ruta'] = []
                    st.session_state['ruta_calculada'] = None
                    st.session_state['contador_ubicaciones'] = 0
                elif opcion == "👤 Perfil":
                    # Entrar al perfil siempre cierra los mapas que estuvieras viendo
                    st.session_state['modo_mapa'] = 'crear'
                    st.session_state['ruta_activa_id'] = None
                
                st.rerun()
            
            st.divider()
            if st.button("Cerrar Sesión"):
                st.session_state['usuario_logueado'] = None
                st.session_state['pagina_actual'] = "🏠 Feed" 
                st.session_state['pantalla_actual'] = "Login" 
                st.rerun()
                
        # 4. Renderizado de la vista seleccionada
        if st.session_state['pagina_actual'] == "🏠 Feed":
            home_view.render()
            
        elif st.session_state['pagina_actual'] == "🔍 Explorar":
            search_view.render_search()
            
        elif st.session_state['pagina_actual'] == "📍 Crear ruta":
            map_view.render()
            
        elif st.session_state['pagina_actual'] == "💬 Chat":
            chat_view.render()
            
        elif st.session_state['pagina_actual'] == "👤 Perfil":
            id_actual = st.session_state['usuario_logueado']['id']
            profile_view.render_profile(id_actual)

if __name__ == "__main__":
    main()