import streamlit as st
from negocio import home_service

def render():
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
            with st.container(border=True):
                
                # 1. Cabecera
                st.markdown(f"**@{ruta['username']}** • {ruta['fecha_bonita']}")
                
                # 2. Imagen
                try:
                    st.image(ruta['imagen_bytes'], use_container_width=True)
                except Exception:
                    st.error("No se pudo cargar la imagen.")
                
               # 3. Título y Etiquetas (desde un array real)
                # Obtenemos la lista directamente (ej: ['montaña', 'dificil'])
                etiquetas_crudas = ruta.get('tags') 
                tags_html = ""
                
                # Comprobamos que no venga nulo ni vacío
                if etiquetas_crudas and isinstance(etiquetas_crudas, list):
                    # Como ya es una lista, solo le añadimos el "#" a cada elemento y los unimos con un espacio
                    tags_format = " ".join([f"#{t.strip()}" for t in etiquetas_crudas if t.strip()])
                    tags_html = f"<span style='font-size: 0.5em; color: #888; font-weight: normal; margin-left: 10px;'>{tags_format}</span>"
                
                st.markdown(f"### {ruta['name']} {tags_html}", unsafe_allow_html=True)
                
                # 4. Descripción
                if ruta.get('description'):
                    st.write(ruta['description'])
                    
                # 5. Likes (Corazón mini y texto popover)
                col_like, col_text_likes = st.columns([1, 10]) 
                
                with col_like:
                    corazon = "❤️" if ruta.get('user_has_liked') else "🤍"
                    if st.button(corazon, key=f"like_{ruta['id']}"):
                        home_service.gestionar_like(usuario['id'], ruta['id'], ruta.get('user_has_liked'))
                        st.rerun()
                        
                with col_text_likes:
                    with st.popover(f"{ruta.get('num_likes', 0)} Me gusta", use_container_width=False):
                        usuarios_like = home_service.obtener_nombres_likes(ruta['id'])
                        if usuarios_like:
                            for u in usuarios_like:
                                st.markdown(f"👤 **@{u['username']}**")
                        else:
                            st.caption("Aún no hay likes.")

                # 6. Comentarios (Formulario para limpiar el input automáticamente)
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
                            home_service.publicar_comentario(usuario['id'], ruta['id'], nuevo_comentario)
                            st.rerun()