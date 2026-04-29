import streamlit as st
from negocio import home_service

def render_publication(ruta, usuario):
    """
    Renderiza una única publicación (tarjeta de ruta).
    """
    with st.container(border=True):
        # 1. Cabecera: Nombre de usuario y Fecha
        col_u, col_f = st.columns([3, 1])
        
        with col_u:
            nombre_user = ruta.get('username', 'Usuario')
            id_creador = ruta.get('creator_id') 
            
            # Redirección a Explorar para ver perfil ajeno
            if st.button(f"@{nombre_user}", key=f"user_link_{ruta['id']}"):
                if id_creador:
                    st.session_state['perfil_a_ver'] = id_creador
                    st.session_state['pagina_actual'] = "🔍 Explorar"
                    st.rerun()
                else:
                    st.warning("No se pudo obtener el ID de este usuario.")
        
        with col_f:
            st.markdown(f"<p style='text-align: right; color: gray;'>{ruta.get('fecha_bonita', 'Reciente')}</p>", unsafe_allow_html=True)
        
        # 2. Imagen de la ruta
        try:
            st.image(ruta['imagen_bytes'], use_container_width=True)
        except Exception:
            st.error("No se pudo cargar la imagen.")
        
        # 3. Título y Etiquetas (Tags)
        etiquetas_crudas = ruta.get('tags') 
        tags_html = ""
        
        if etiquetas_crudas and isinstance(etiquetas_crudas, list):
            tags_format = " ".join([f"#{t.strip()}" for t in etiquetas_crudas if t.strip()])
            tags_html = f"<span style='font-size: 0.6em; color: #888; font-weight: normal; margin-left: 10px;'>{tags_format}</span>"
        
        st.markdown(f"### {ruta.get('name', 'Sin nombre')} {tags_html}", unsafe_allow_html=True)
        
        # 4. Descripción
        if ruta.get('description'):
            st.write(ruta['description'])
        
        st.divider()

        # 5. Interacciones: Likes y Favoritos
        col_like, col_fav, col_text_likes = st.columns([1, 1, 8]) 
        
        with col_like:
            liked = ruta.get('user_has_liked')
            # 🚀 Corazón ROJO si tiene like, BLANCO si no
            corazon = "❤️" if liked else "🤍"
            if st.button(corazon, key=f"like_{ruta['id']}"):
                home_service.gestionar_like(usuario['id'], ruta['id'], liked)
                st.rerun()
        
        with col_fav:
            es_fav = ruta.get('user_has_favorited')
            # 🚀 Estrella AMARILLA si está guardado, BLANCA/HUECA si no
            estrella = "⭐" if es_fav else "☆"
            if st.button(estrella, key=f"fav_{ruta['id']}"):
                home_service.gestionar_favorito(usuario['id'], ruta['id'], es_fav)
                st.rerun()
                
        with col_text_likes:
            with st.popover(f"{ruta.get('num_likes', 0)} Me gusta", use_container_width=False):
                usuarios_like = home_service.obtener_nombres_likes(ruta['id'])
                if usuarios_like:
                    for u in usuarios_like:
                        st.markdown(f"👤 **@{u['username']}**")
                else:
                    st.caption("Aún no hay likes.")

        # 6. Sección de Comentarios
        with st.expander("💬 Comentarios"):
            comentarios = home_service.obtener_comentarios_ruta(ruta['id'])
            if comentarios:
                for c in comentarios:
                    st.markdown(f"**@{c['username']}**: {c['content']}")
            else:
                st.caption("No hay comentarios todavía.")
            
            st.write("") 
            
            # Formulario para enviar comentario
            with st.form(key=f"form_comm_{ruta['id']}", clear_on_submit=True, border=False):
                col_input, col_btn = st.columns([4, 1])
                
                with col_input:
                    nuevo_comentario = st.text_input("Añade un comentario...", label_visibility="collapsed")
                with col_btn:
                    submit_btn = st.form_submit_button("Enviar", use_container_width=True)
                    
                if submit_btn and nuevo_comentario.strip():
                    home_service.publicar_comentario(usuario['id'], ruta['id'], nuevo_comentario)
                    st.rerun()

        # 7. Botón para ver ruta o modificar
        st.divider()
        col_ver, col_mod = st.columns(2)
        
        with col_ver:
            if st.button("🗺️ Ver en Mapa", use_container_width=True, key=f"ver_map_{ruta['id']}"):
                st.session_state['modo_mapa'] = 'ver'
                st.session_state['ruta_activa_id'] = ruta['id']
                st.session_state['pagina_actual'] = "📍 Crear ruta" # Viajamos al mapa
                st.rerun()

        with col_mod:
            if st.button("🛠️ Modificar Ruta", use_container_width=True, key=f"mod_map_{ruta['id']}"):
                # Aquí está el truco: le decimos que vamos a editar
                st.session_state['modo_mapa'] = 'editar'
                st.session_state['ruta_activa_id'] = ruta['id']
                st.session_state['pagina_actual'] = "📍 Crear ruta"
                st.rerun()

def render():
    """
    Función principal de la vista Home.
    """
    st.title("📱 Mi Feed")

    usuario = st.session_state.get('usuario_logueado')
    
    if not usuario:
        st.error("Error: No se ha iniciado sesión correctamente.")
        return

    # Obtenemos las rutas del feed
    rutas_feed = home_service.obtener_feed_usuario(usuario['id'])

    if not rutas_feed:
        st.info("Aún no sigues a nadie o tus amigos no han publicado nada.")
    else:
        for ruta in rutas_feed:
            # Llamamos a la función encargada de renderizar cada publicación
            render_publication(ruta, usuario)