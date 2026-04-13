import streamlit as st
from negocio import home_service

def render():
    usuario = st.session_state['usuario_logueado']
    
    st.title(f"📱 Feed de @{usuario['nombre']}")
    st.write("---")

    rutas_feed = home_service.obtener_feed_usuario(usuario['id'])

    if not rutas_feed:
        st.info("Aún no sigues a nadie o tus amigos no han publicado nada.")
        return

    col_izq, col_centro, col_der = st.columns([1, 2, 1])

    with col_centro:
        for ruta in rutas_feed:
            with st.container(border=True): 
                # 1. Cabecera
                st.markdown(f"**@{ruta['username']}** • {ruta['fecha_bonita']}")
                
                # 2. Miniatura
                try: 
                    st.image(ruta['imagen_bytes'], use_container_width=True)
                except Exception: 
                    st.error("No se pudo cargar la imagen.")
                
                # 3. Título y descripción
                st.subheader(ruta['name'])
                if ruta['description']: st.write(ruta['description'])
                
                # 4. Likes y Acciones
                col_like_btn, col_like_count, col_ver_likes = st.columns([1, 1, 2])
                with col_like_btn:
                    icono_like = "❤️" if ruta['mi_like'] else "🤍"
                    if st.button(f"{icono_like} Like", key=f"btn_like_{ruta['id']}", use_container_width=True):
                        home_service.gestionar_like(usuario['id'], ruta['id'], ruta['mi_like'])
                        st.rerun() 
                        
                with col_like_count:
                    st.write(f"**{ruta['num_likes']} Me gusta**")
                    
                with col_ver_likes:
                    with st.popover("👥 Ver likes"):
                        usuarios_like = home_service.obtener_nombres_likes(ruta['id'])
                        if usuarios_like:
                            for u in usuarios_like: st.write(f"• @{u}")
                        else: st.write("Aún no hay likes.")

                # 🚀 5. COMENTARIOS REALES
                # 🚀 SECCIÓN DE COMENTARIOS CON FORMULARIO
                with st.expander("💬 Comentarios"):
                    # 1. Cargamos los comentarios existentes
                    comentarios = home_service.obtener_comentarios_ruta(ruta['id'])
                    if comentarios:
                        for c in comentarios:
                            st.markdown(f"**@{c['username']}**: {c['content']}")
                    else:
                        st.caption("No hay comentarios todavía.")
                    
                    st.write("---")
                    
                    # 2. El Formulario Mágico (clear_on_submit=True lo limpia todo solo)
                    with st.form(key=f"form_comm_{ruta['id']}", clear_on_submit=True, border=False):
                        # Ponemos el input y el botón en la misma línea
                        col_input, col_btn = st.columns([4, 1])
                        
                        with col_input:
                            nuevo_comentario = st.text_input("Escribe aquí...", label_visibility="collapsed")
                        with col_btn:
                            submit_btn = st.form_submit_button("Enviar", use_container_width=True)
                            
                        # Si pulsa el botón y hay texto
                        if submit_btn and nuevo_comentario.strip():
                            # Guardamos en la BBDD
                            home_service.publicar_comentario(usuario['id'], ruta['id'], nuevo_comentario)
                            # Refrescamos la pantalla para ver el nuevo comentario
                            st.rerun()

                # 6. Botones de Acción de Ruta
                col_ver, col_mod = st.columns(2)
                with col_ver:
                    if st.button("👁️ Ver ruta en mapa", key=f"ver_{ruta['id']}", use_container_width=True):
                        st.session_state['ruta_activa_id'] = ruta['id']
                        st.session_state['modo_mapa'] = 'ver'
                        st.session_state['pagina_actual'] = 'mapa'
                        st.rerun()
                with col_mod:
                    if st.button("✏️ Modificar ruta", key=f"mod_{ruta['id']}", use_container_width=True):
                        st.session_state['ruta_activa_id'] = ruta['id']
                        st.session_state['modo_mapa'] = 'modificar'
                        st.session_state['pagina_actual'] = 'mapa'
                        st.rerun()

            st.write("")