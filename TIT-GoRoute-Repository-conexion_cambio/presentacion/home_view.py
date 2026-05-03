import streamlit as st
from negocio import home_service

def render_publication(ruta, usuario_logueado):
    """
    Renderiza una única publicación (tarjeta de ruta).
    """
    # Inyectamos CSS para que los botones de usuario parezcan enlaces limpios
    st.markdown("""
        <style>
        .stButton > button[key^="user_link_"] {
            border: none;
            background: transparent;
            color: #4CAF50;
            padding: 0;
            font-weight: bold;
            font-size: 1.1em;
            text-align: left;
        }
        .stButton > button[key^="user_link_"]:hover {
            color: #388E3C;
            text-decoration: underline;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        # 1. Cabecera: Nombre de usuario y Fecha
        col_u, col_f = st.columns([3, 1])
        
        with col_u:
            nombre_user = ruta.get('username', 'Usuario')
            id_creador = ruta.get('creator_id') 
            
            # --- CAMBIO CLAVE: Navegación al perfil ajeno ---
            if st.button(f"@{nombre_user}", key=f"user_link_{ruta['id']}"):
                if id_creador:
                    # Seteamos el ID del perfil que queremos ver
                    st.session_state['perfil_a_ver'] = id_creador
                    # Nos aseguramos de estar en la página de Explorar que es la que gestiona esto
                    st.session_state['pagina_actual'] = "🔍 Explorar"
                    st.rerun()
                else:
                    st.warning("No se pudo obtener el ID de este usuario.")
        
        with col_f:
            st.markdown(f"<p style='text-align: right; color: gray;'>{ruta.get('fecha_bonita', 'Reciente')}</p>", unsafe_allow_html=True)
        
        # 2. Imagen de la ruta
        try:
            if ruta.get('imagen_bytes'):
                st.image(ruta['imagen_bytes'], use_container_width=True)
            else:
                st.image("https://images.unsplash.com/photo-1551632811-561732d1e306?q=80&w=1000", use_container_width=True)
        except Exception:
            st.error("No se pudo cargar la imagen.")
        
        # 3. Título y Etiquetas (Tags)
        etiquetas_crudas = ruta.get('tags') 
        tags_html = ""
        
        if etiquetas_crudas and isinstance(etiquetas_crudas, list):
            tags_format = " ".join([f"#{t.strip()}" for t in etiquetas_crudas if t.strip()])
            tags_html = f"<span style='font-size: 0.6em; color: #888; font-weight: normal; margin-left: 10px;'>{tags_format}</span>"
        
        # Usamos 'name' o 'nombre' según devuelva tu base de datos
        titulo = ruta.get('nombre') or ruta.get('name') or "Sin nombre"
        st.markdown(f"### {titulo} {tags_html}", unsafe_allow_html=True)
        
        # 4. Descripción
        if ruta.get('description') or ruta.get('descripcion'):
            desc = ruta.get('description') or ruta.get('descripcion')
            st.write(desc)
        
        st.divider()

        # 5. Interacciones: Likes y Favoritos (¡AQUÍ ESTÁ LA MAGIA CORREGIDA!)
        col_like, col_fav, col_text_likes = st.columns([1, 1, 8]) 
        
        # Obtenemos el estado real en vivo desde la base de datos
        estado_like, estado_fav = home_service.obtener_estado_interacciones(ruta['id'], usuario_logueado['id'])
        
        with col_like:
            corazon = "❤️" if estado_like else "🤍"
            if st.button(corazon, key=f"like_{ruta['id']}"):
                home_service.gestionar_like(usuario_logueado['id'], ruta['id'], estado_like)
                st.rerun()
        
        with col_fav:
            estrella = "⭐" if estado_fav else "☆"
            if st.button(estrella, key=f"fav_{ruta['id']}"):
                home_service.gestionar_favorito(usuario_logueado['id'], ruta['id'], estado_fav)
                st.rerun()
                
        with col_text_likes:
            num_likes = ruta.get('num_likes', 0)
            with st.popover(f"{num_likes} Me gusta", use_container_width=False):
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
            
            with st.form(key=f"form_comm_{ruta['id']}", clear_on_submit=True, border=False):
                col_input, col_btn = st.columns([4, 1])
                with col_input:
                    nuevo_comentario = st.text_input("Añade un comentario...", label_visibility="collapsed")
                with col_btn:
                    submit_btn = st.form_submit_button("Enviar", use_container_width=True)
                    
                if submit_btn and nuevo_comentario.strip():
                    home_service.publicar_comentario(usuario_logueado['id'], ruta['id'], nuevo_comentario)
                    st.rerun()

        # 7. Botones de Mapa (Ver/Modificar)
        st.divider()
        col_ver, col_mod = st.columns(2)
        
        with col_ver:
            if st.button("🗺️ Ver en Mapa", use_container_width=True, key=f"ver_map_{ruta['id']}"):
                st.session_state['modo_mapa'] = 'ver'
                st.session_state['ruta_activa_id'] = ruta['id']
                st.session_state['pagina_actual'] = "📍 Crear ruta"
                st.rerun()

        with col_mod:
            # Verificamos si el usuario actual es el dueño
            es_dueno = (id_creador == usuario_logueado['id'])
            
            # El texto cambia según la intención, pero el botón SIEMPRE es clicable
            texto_boton = "🛠️ Editar mi Ruta" if es_dueno else "✨ Modificar Ruta"
            color_ayuda = "Puedes modificar tu propia ruta." if es_dueno else "Vas a crear una copia de esta ruta para modificarla a tu gusto."

            if st.button("🛠️ Modificar Ruta", use_container_width=True, key=f"mod_map_{ruta['id']}"):
                # Aquí está el truco: le decimos que vamos a editar
                st.session_state['modo_mapa'] = 'editar'
                st.session_state['ruta_activa_id'] = ruta['id']
                st.session_state['pagina_actual'] = "📍 Crear ruta"
                st.rerun()

def render():
    """
    Función principal de la vista Home (Feed).
    """
    st.title("📱 Mi Feed")

    usuario = st.session_state.get('usuario_logueado')
    
    if not usuario:
        st.error("Error: No se ha iniciado sesión correctamente.")
        return

    rutas_feed = home_service.obtener_feed_usuario(usuario['id'])

    if not rutas_feed:
        st.info("Aún no sigues a nadie o tus amigos no han publicado nada.")
    else:
        for ruta in rutas_feed:
            render_publication(ruta, usuario)