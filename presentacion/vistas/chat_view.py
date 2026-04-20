# presentacion/vistas/chat_view.py
import streamlit as st
from negocio import chat_service

# --- FRAGMENTO 1: LISTA DE CHATS (Se actualiza cada 2 segundos) ---
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


# --- FRAGMENTO 2: MENSAJES EN VIVO (Se actualiza cada 1 segundo) ---
@st.fragment(run_every="1s")
def renderizar_mensajes_en_vivo(current_user_id, otro_usuario_id, limite_mensajes):
    mensajes = chat_service.obtener_historial_chat(
        current_user_id, 
        otro_usuario_id, 
        offset=0,           # <-- Siempre empezamos desde el más reciente
        limit=limite_mensajes # <-- Lo que aumentamos es el número máximo de mensajes visibles
    )
    
    # Altura fija para la caja de chat con scroll automático
    contenedor_chat = st.container(height=500) 
    
    with contenedor_chat:
        if not mensajes:
            st.info("No hay mensajes todavía. ¡Di hola!")
        else:
            for msg in mensajes:
                if msg['sender_id'] == current_user_id:
                    with st.chat_message("user"):
                        st.write(msg['content'])
                else:
                    with st.chat_message("assistant", avatar="👤"):
                        st.write(msg['content'])
# -----------------------------------------------------------------


def render_chat_view():
    st.markdown("## 💬 Centro de Mensajes")
    current_user_id = st.session_state.get('user_id', 1) 
    
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
        
        # Llamamos al Fragmento 1 (Hará su trabajo en segundo plano)
        renderizar_lista_chats_activos(current_user_id)

    # COLUMNA DERECHA: Ventana de Chat
    with col_ventana:
        if st.session_state.chat_activo:
            otro_usuario = st.session_state.chat_activo
            st.markdown(f"### Conversación con {otro_usuario['username']}")
            
            # Botón de Paginación para ver mensajes viejos
            if st.button("↑ Cargar mensajes anteriores", use_container_width=True):
                # Aumentamos el límite de mensajes a mostrar (de 50 a 100, etc.)
                st.session_state.chat_limit += 50
                st.rerun()
                    
            st.markdown("---")
            
            # Llamada al Fragmento 2 (Hará su trabajo en segundo plano)
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