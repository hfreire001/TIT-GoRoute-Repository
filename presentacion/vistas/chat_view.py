# vistas/chat_view.py
import streamlit as st
from negocio import chat_service

def render_chat_view():
    st.markdown("## 💬 Mensajes")
    
    # Asumimos que el ID del usuario actual está en la sesión tras el login
    current_user_id = st.session_state.get('user_id', 1) 
    
    # Variables de estado para el chat activo y el scroll de paginación
    if 'chat_activo' not in st.session_state:
        st.session_state.chat_activo = None
    if 'chat_offset' not in st.session_state:
        st.session_state.chat_offset = 0

    # CSS Personalizado para alinear mensajes (Derecha = principal, Izquierda = el otro)
    st.markdown("""
    <style>
    .msg-der { text-align: right; background-color: #0056b3; color: white; padding: 10px 15px; border-radius: 15px 15px 0px 15px; margin: 5px; margin-left: auto; max-width: 80%; width: fit-content; font-family: sans-serif;}
    .msg-izq { text-align: left; background-color: #e9ecef; color: black; padding: 10px 15px; border-radius: 15px 15px 15px 0px; margin: 5px; margin-right: auto; max-width: 80%; width: fit-content; font-family: sans-serif;}
    </style>
    """, unsafe_allow_html=True)

    # Layout: Columna izquierda (Lista de chats/Buscador) y Columna derecha (Ventana del chat)
    # Al estar en móvil, Streamlit automáticamente apilará la columna 1 encima de la 2 adaptativamente.
    col_lista, col_ventana = st.columns([1, 2])
    
    with col_lista:
        st.subheader("Buscar Usuario")
        # El buscador se actualiza según se escribe gracias al text_input de Streamlit
        buscador = st.text_input("Buscar por @username...", placeholder="Ej: pedro_plango")
        
        if buscador:
            resultados = chat_service.buscar_usuarios_activos(current_user_id, buscador)
            for usuario in resultados:
                # Indicador visual si priorizamos porque lo seguimos
                seguido_tag = "🌟 (Siguiendo)" if usuario['is_followed'] else ""
                if st.button(f"👤 {usuario['username']} {seguido_tag}", key=f"busqueda_{usuario['user_id']}"):
                    st.session_state.chat_activo = usuario
                    st.session_state.chat_offset = 0
                    st.rerun()
                    
        st.markdown("---")
        st.subheader("Tus Chats")
        lista_chats = chat_service.obtener_chats_recientes(current_user_id)
        
        if not lista_chats:
            st.info("No tienes ningún chat todavía. Usa el buscador de arriba para iniciar uno nuevo.")
        else:
            for chat in lista_chats:
                # Mostramos los chats ordenados del más reciente al más antiguo
                if st.button(f"💬 {chat['username']} \n\n _{chat['last_message'][:25]}..._", use_container_width=True, key=f"historial_{chat['user_id']}"):
                    st.session_state.chat_activo = {"user_id": chat['user_id'], "username": chat['username']}
                    st.session_state.chat_offset = 0
                    st.rerun()

    with col_ventana:
        if st.session_state.chat_activo:
            otro_usuario = st.session_state.chat_activo
            st.markdown(f"### Chat con {otro_usuario['username']}")
            
            # Botón superior que emula el "Scroll hacia arriba" para cargar 50 mensajes más
            col_spacer1, col_btn, col_spacer2 = st.columns([1,2,1])
            with col_btn:
                if st.button("↑ Cargar mensajes anteriores", use_container_width=True):
                    st.session_state.chat_offset += 50
                    st.rerun()
                    
            st.markdown("---")
            
            # Obtención dinámica de los mensajes con el rango correspondiente (Máx 50 por bloque)
            mensajes = chat_service.obtener_historial_chat(
                current_user_id, 
                otro_usuario['user_id'], 
                offset=st.session_state.chat_offset, 
                limit=50
            )
            
            # Renderizado de la conversación
            for msg in mensajes:
                if msg['sender_id'] == current_user_id:
                    st.markdown(f"<div class='msg-der'>{msg['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='msg-izq'>{msg['content']}</div>", unsafe_allow_html=True)
            
            # El input para escribir se encuentra permanentemente abajo
            nuevo_mensaje = st.chat_input("Escribe tu mensaje aquí...")
            
            if nuevo_mensaje:
                chat_service.enviar_mensaje(current_user_id, otro_usuario['user_id'], nuevo_mensaje)
                # Al enviar un mensaje, reseteamos el scroll abajo del todo
                st.session_state.chat_offset = 0 
                st.rerun()
        else:
            st.write("👈 Selecciona un chat de la lista o busca un usuario para empezar a hablar.")