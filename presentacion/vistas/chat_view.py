# presentacion/vistas/chat_view.py
import streamlit as st
from negocio import chat_service

# --- COLORES IDENTIDAD ---
AZUL_PROFUNDO = "#003366"
AZUL_SUAVE = "#F0F4F8"
AZUL_MEDIO = "#518AC4"  

def inyectar_estilos_chat():
    st.markdown(f"""
        <style>
          /* Título principal */
            h2 {{
                color: {AZUL_PROFUNDO} !important;
                font-size: 2.1rem !important; /* Un poco más pequeño que el default */
            }}
            
            /* Subtítulos (Buscar Usuarios, Conversación con..., Tus Chats) */
            h3 {{
                color: {AZUL_PROFUNDO} !important;
                font-size: 1.0rem !important; /* Tamaño reducido */
                font-weight: 600;
                margin-bottom: 10px;
            }}
            
            /* --- EL CAMBIO PARA EL TEXTO AZUL EN LA LISTA IZQUIERDA --- */
            /* Esto busca el texto en cursiva (_) dentro de los botones de la lista */
            .stButton > button em {{
                color: {AZUL_MEDIO} !important;
                font-style: normal !important; /* Si quieres que no sea cursiva, sino solo azul */
                font-weight: 500;
                font-size: 0.8rem !important;
            }}
            
            /* Nombre de usuario en el botón (el texto que no es cursiva) */
            .stButton > button p {{
                color: {AZUL_PROFUNDO};
                font-weight: bold;
            }}
            
            /* Ajuste de los mensajes nativos de Streamlit */
            [data-testid="stChatMessage"] {{
                background-color: {AZUL_SUAVE};
                border-radius: 15px;
                padding: 10px;
                margin-bottom: 10px;
            }}
            
            /* 1. Mensajes del OTRO USUARIO (Azul clarito) */
            [data-testid="stChatMessage"]:has(div[data-testid="stChatMessageContent"] p) {{
                background-color: #E8F1F9 !important;
                border-radius: 15px;
                border: 1px solid #D0E2F2;
            }}

            /* 2. MIS MENSAJES (Azul fuerte / Profundo) */
            /* Streamlit marca los mensajes del usuario con un estilo específico, lo aprovechamos */
            [data-testid="stChatMessage"]:has(div:contains("user")) {{
                background-color: {AZUL_PROFUNDO} !important;
                color: white !important;
                border-radius: 15px;
            }}
            
            /* Forzar el color de texto blanco en mis mensajes */
            [data-testid="stChatMessage"]:has(div:contains("user")) p {{
                color: white !important;
            }}
            

            /* Botones de la lista lateral */
            .stButton > button {{
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                transition: all 0.3s;
            }}
            
            .stButton > button:hover {{
                border-color: {AZUL_PROFUNDO};
                background-color: #f7f9fc;
            }}
    """, unsafe_allow_html=True)


@st.fragment(run_every="2s")
def renderizar_lista_chats_activos(current_user_id):
    st.subheader("📬 Tus Chats Recientes")
    lista_chats = chat_service.obtener_chats_recientes(current_user_id)
    
    if not lista_chats:
        st.write("Aún no tienes chats activos.")
    else:
        for chat in lista_chats:
            # Si alguien pulsa en un chat, cambiamos la sesión y forzamos recarga general
            if st.button(f"👤 {chat['username']} \n\n _{chat['last_message'][:25]}..._", key=f"hist_{chat['user_id']}", use_container_width=True):
                st.session_state.chat_activo = {"user_id": chat['user_id'], "username": chat['username']}
                st.session_state.chat_limit = 50 # Reseteamos la cantidad de mensajes al entrar
                st.rerun()
# -----------------------------------------------------------------



# --- FRAGMENTO 2: MENSAJES EN VIVO (Corrección de duplicado) ---
@st.fragment(run_every="1s")
def renderizar_mensajes_en_vivo(current_user_id, otro_usuario_id, limite_mensajes):
    mensajes = chat_service.obtener_historial_chat(
        current_user_id, 
        otro_usuario_id, 
        offset=0,
        limit=limite_mensajes
    )
    
    # CSS extra para eliminar el fondo gris nativo de Streamlit y que no se vea doble
    st.markdown("""
        <style>
            /* Quitamos el fondo y borde a la burbuja original de Streamlit */
            [data-testid="stChatMessage"] {
                background-color: transparent !important;
                border: none !important;
            }
            /* Quitamos el padding extra para que nuestra burbuja encaje bien */
            [data-testid="stChatMessageContent"] {
                padding: 0px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    contenedor_chat = st.container(height=500) 
    
    with contenedor_chat:
        if not mensajes:
            st.info("No hay mensajes todavía. ¡Di hola!")
        else:
            for msg in mensajes:
                es_mio = msg['sender_id'] == current_user_id
                
                if es_mio:
                    # TUS MENSAJES
                    with st.chat_message("user"):
                        st.markdown(f"""
                            <div style="
                                background-color: {AZUL_PROFUNDO}; 
                                color: white; 
                                padding: 12px 16px; 
                                border-radius: 15px; 
                                width: fit-content;
                                max-width: 90%;
                                margin-left: 0px;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                {msg['content']}
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    # MENSAJES DEL OTRO
                    with st.chat_message("assistant", avatar="👤"):
                        st.markdown(f"""
                            <div style="
                                background-color: #E8F1F9; 
                                color: #262730; 
                                padding: 12px 16px; 
                                border-radius: 15px; 
                                width: fit-content;
                                max-width: 90%;
                                border: 1px solid #D0E2F2;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                                {msg['content']}
                            </div>
                        """, unsafe_allow_html=True)
# -----------------------------------------------------------------


def render_chat_view(current_user_id):
    inyectar_estilos_chat()
    st.markdown("## Centro de Mensajes 💬")
    
    # Inicialización de variables de estado
    if 'chat_activo' not in st.session_state:
        st.session_state.chat_activo = None
        
    # Sustituimos el antiguo offset por el límite de mensajes visibles
    if 'chat_limit' not in st.session_state:
        st.session_state.chat_limit = 50

    col_lista, col_ventana = st.columns([1, 2])
    
    # COLUMNA IZQUIERDA: Buscador y Lista
    with col_lista:
        st.subheader("🔍 Buscar Usuarios")
        buscador = st.text_input("Buscar por nombre de usuario...", placeholder="Ej: pedro_plango")
        
        if buscador:
            resultados = chat_service.buscar_usuarios_activos(current_user_id, buscador)
            for usuario in resultados:
                seguido_tag = "🌟 Siguiendo" if usuario['is_followed'] else ""
                if st.button(f"👤 {usuario['username']} {seguido_tag}", key=f"bus_{usuario['user_id']}", use_container_width=True):
                    st.session_state.chat_activo = usuario
                    st.session_state.chat_limit = 50
                    st.rerun()
                    
        st.markdown("---")
        
        
        renderizar_lista_chats_activos(current_user_id)

    # COLUMNA DERECHA: Ventana de Chat
    with col_ventana:
        if st.session_state.chat_activo:
            otro_usuario = st.session_state.chat_activo
            st.markdown(f"### Conversación con {otro_usuario['username']}")
            
            if st.button("↑ Cargar mensajes anteriores", use_container_width=True):
                # Aumentamos el límite de mensajes a mostrar (de 50 a 100, etc.)
                st.session_state.chat_limit += 50
                st.rerun()
                    
            st.markdown("---")
            
            renderizar_mensajes_en_vivo(
                current_user_id, 
                otro_usuario['user_id'], 
                st.session_state.chat_limit
            )
            
            # Input de texto de Streamlit
            nuevo_mensaje = st.chat_input("Escribe tu mensaje...")
            
            if nuevo_mensaje:
                chat_service.enviar_mensaje(current_user_id, otro_usuario['user_id'], nuevo_mensaje)
                # Al enviar mensaje, volvemos a mostrar solo los 50 últimos para resetear la vista
                st.session_state.chat_limit = 50 
                st.rerun() 
        else:
            st.info("👈 Selecciona un chat de la lista o busca un usuario para empezar a hablar.")