import streamlit as st

# Importamos las vistas principales
from presentacion import login_view, home_view, profile_view, map_view, register_view, search_view
# Importamos el chat desde su subcarpeta
from presentacion.vistas import chat_view

st.set_page_config(page_title="Plan&Go", layout="wide", page_icon="📍")

# --- CAMBIOS DE ESTILIZADO: Inyección de CSS Global ---
# Este bloque aplica el fondo azul profesional al sidebar y ajusta los colores de texto y botones para contraste.
st.markdown(
    """
    <style>
        /* Fondo del sidebar azul oscuro profesional */
        [data-testid="stSidebar"] {
            background-color: #a5c1e6;
            color: white;
        }

        /* Color de texto para markdown en sidebar */
        [data-testid="stSidebar"] .stMarkdown p {
            color: white !important;
        }

        /* Color de texto para etiquetas de radio buttons */
        [data-testid="stSidebar"] .stRadio label p {
            color: white !important;
        }
        
        /* Ajustar el divisor para que sea más visible sobre azul */
        [data-testid="stSidebar"] hr {
            border-color: rgba(255, 255, 255, 0.2) !important;
        }

        /* Estilizar el botón de Cerrar Sesión (blanco con texto azul) */
        [data-testid="stSidebar"] .stButton button {
            color: #003366 !important;
            background-color: white !important;
            border: 1px solid white !important;
            width: 100%;
        }
        [data-testid="stSidebar"] .stButton button:hover {
            background-color: #f0f2f6 !important;
            color: #002244 !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)
# --------------------------------------------------

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
            # --- CAMBIOS DE ESTILIZADO: Logo de la app arriba ---
            # Asegúrate de que tu logo esté guardado en 'assets/logo.png' (o cambia la ruta aquí)
            try:
                # Usamos use_container_width para que se adapte al ancho del sidebar
                st.image("assets/logo2.png", use_container_width=True)
            except FileNotFoundError:
                st.warning("⚠️ No se encontró el logo en 'assets/logo.png'. Por favor, verifica la ruta o coloca la imagen.")
            
            st.divider()
            # ----------------------------------------------------

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
                    # 1. Cierra los mapas que estuvieras viendo
                    st.session_state['modo_mapa'] = 'crear'
                    st.session_state['ruta_activa_id'] = None
                    # 🚀 2. ESTO ES LO NUEVO: Fuerza al perfil a volver a la cuadrícula inicial
                    st.session_state['modo_perfil'] = 'grid'
                elif opcion == "🔍 Explorar":
                    # Igual si usas el mismo sistema en buscar, te aseguras de limpiar
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
            id_actual = st.session_state['usuario_logueado']['id']
            chat_view.render_chat_view(id_actual)
            
        elif st.session_state['pagina_actual'] == "👤 Perfil":
            id_actual = st.session_state['usuario_logueado']['id']
            profile_view.render_profile(id_actual)

if __name__ == "__main__":
    main()