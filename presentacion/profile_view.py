import streamlit as st
from negocio import profile_service
import base64
import os
from presentacion import home_view  
from datos import route_repo # 🚀 Importamos esto para coger los tags y descripción

def get_image_base64(path):
    if path and os.path.exists(path):
        try:
            with open(path, "rb") as f:
                data = f.read()
            ext = path.split('.')[-1].lower()
            return f"data:image/{ext};base64,{base64.b64encode(data).decode()}"
        except Exception:
            return None
    return None

import streamlit as st
from negocio import profile_service
from presentacion import home_view
import base64
import os

def get_image_base64(path):
    """Convierte una imagen en base64 para mostrarla en HTML."""
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
            return f"data:image/png;base64,{encoded}"
    except:
        return None

def render_profile(user_id):
    # Control de navegación interna del perfil
    if 'modo_perfil' not in st.session_state:
        st.session_state['modo_perfil'] = 'grid'

    modo = st.session_state['modo_perfil']
    usuario_logueado = st.session_state.get('usuario_logueado')

    # 1. ESTILOS CSS (Para que la cuadrícula y el hover funcionen)
    st.markdown("""
        <style>
            .avatar-container { display: flex; justify-content: center; margin-bottom: 20px; }
            .avatar-circle {
                width: 150px; height: 150px;
                border-radius: 50%; object-fit: cover;
                border: 3px solid #4CAF50;
            }
            .route-card {
                background-color: #f9f9f9; border-radius: 10px;
                padding: 5px; text-align: center; margin-bottom: 10px;
                border: 1px solid #ddd;
            }
            .img-container {
                position: relative; width: 100%; height: 150px;
                border-radius: 8px; overflow: hidden;
            }
            .route-img-fixed {
                width: 100%; height: 100%; object-fit: cover;
            }
            .overlay {
                position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0, 0, 0, 0.7); color: white;
                display: flex; justify-content: center; align-items: center;
                gap: 10px; opacity: 0; transition: 0.3s;
            }
            .img-container:hover .overlay { opacity: 1; }
            .stat-item { display: flex; flex-direction: column; font-size: 0.8em; }
            .route-title { font-weight: bold; margin-top: 5px; font-size: 0.9em; }
        </style>
    """, unsafe_allow_html=True)

    # 2. MODO PUBLICACIÓN INDIVIDUAL (Cuando haces clic en "Ver")
    if modo == 'publicacion' and 'ruta_ver_publicacion' in st.session_state:
        ruta_p = st.session_state['ruta_ver_publicacion']
        
        if st.button("⬅️ Volver al Perfil"):
            st.session_state['modo_perfil'] = 'grid'
            st.rerun()

        st.divider()
        
        # Obtenemos estado real de interacciones para pintar botones rojo/amarillo
        h_liked, h_fav = False, False
        if usuario_logueado:
            h_liked, h_fav = profile_service.obtener_estado_interacciones(ruta_p['id'], usuario_logueado['id'])
        
        # En la parte if modo == 'publicacion':
        ruta_adaptada = {
            'id': ruta_p['id'],
            'username': usuario_logueado['username'] if usuario_logueado else "Usuario",
            'creator_id': user_id,
            'name': ruta_p.get('nombre'),
            'description': ruta_p.get('description', 'Sin descripción'), # 🚀 Aquí leemos el real
            'tags': ruta_p.get('tags', []),                              # 🚀 Aquí leemos las reales
            'imagen_bytes': get_image_base64(ruta_p.get('miniatura')),
            'num_likes': ruta_p.get('likes', 0),
            'user_has_liked': h_liked,
            'user_has_favorited': h_fav
        }
        
        home_view.render_publication(ruta_adaptada, usuario_logueado)
        return

    # 3. MODO CUADRÍCULA (Perfil Principal)
    user = profile_service.get_full_profile(user_id)
    if not user:
        st.error("No se encontró el usuario.")
        return

    # Cabecera del perfil
    col_f, col_i = st.columns([1, 2])
    with col_f:
        avatar_src = get_image_base64(user["foto"]) or "https://www.w3schools.com/howto/img_avatar.png"
        st.markdown(f'<div class="avatar-container"><img src="{avatar_src}" class="avatar-circle"></div>', unsafe_allow_html=True)
    
    with col_i:
        st.title(user["username"])
        m1, m2, m3 = st.columns(3)
        m1.metric("Seguidores", user["seguidores"])
        m2.metric("Seguidos", user["seguidos"])
        m3.metric("Rutas", len(user["rutas"]))
        st.write(f"**Bio:** {user['bio'] if user['bio'] else 'Sin biografía.'}")
   
    # 🚀 POP-UP DE EDICIÓN MEJORADO
        with st.popover("✏️ Editar Perfil", use_container_width=True):
            st.subheader("Configuración de Perfil")
            with st.form("edit_profile_form", border=False):
                # Campos con valores actuales por defecto
                new_username = st.text_input("Nombre de usuario", value=user["username"])
                
                # El email ahora se carga desde el diccionario 'user' que devuelve el servicio
                current_email = user.get("email", "")
                new_email = st.text_input("Correo electrónico", value=current_email)
                
                new_bio = st.text_area("Biografía", value=user["bio"])
                
                st.write("---")
                st.caption("Solo rellena si deseas cambiar:")
                new_pass = st.text_input("Nueva contraseña", type="password", placeholder="Dejar vacío para no cambiar")
                new_img = st.file_uploader("Actualizar foto de perfil", type=["png", "jpg", "jpeg"])
                
                if st.form_submit_button("Guardar cambios", type="primary", use_container_width=True):
                    # Validamos que al menos los campos obligatorios no estén vacíos por error
                    if not new_username or not new_email:
                        st.warning("El nombre de usuario y el email no pueden estar vacíos.")
                    else:
                        success = profile_service.actualizar_perfil_completo(
                            user_id, new_username, new_email, new_bio, new_pass, new_img
                        )
                        if success:
                            # Actualizamos la sesión para que el cambio sea instantáneo en toda la app
                            st.session_state['usuario_logueado']['username'] = new_username
                            st.success("¡Perfil actualizado!")
                            st.rerun()
                        else:
                            st.error("Error al actualizar. Verifica si el usuario o email ya existen.")

    st.divider()
    st.subheader("📍 Mis Rutas Publicadas")

    # Cuadrícula de fotos
    if not user["rutas"]:
        st.info("Aún no has publicado ninguna ruta.")
    else:
        cols = st.columns(3)
        for i, ruta in enumerate(user["rutas"]):
            with cols[i % 3]:
                r_src = get_image_base64(ruta.get("miniatura")) or "https://via.placeholder.com/300"
                
                # Renderizado de la tarjeta con contadores
                st.markdown(f'''
                    <div class="route-card">
                        <div class="img-container">
                            <img src="{r_src}" class="route-img-fixed">
                            <div class="overlay">
                                <div class="stat-item"><span>❤️</span><span>{ruta.get('likes', 0)}</span></div>
                                <div class="stat-item"><span>💬</span><span>{ruta.get('comentarios', 0)}</span></div>
                                <div class="stat-item"><span>⭐</span><span>{ruta.get('guardados', 0)}</span></div>
                            </div>
                        </div>
                        <div class="route-title">{ruta.get('nombre', 'Sin nombre')}</div>
                    </div>
                ''', unsafe_allow_html=True)
                
                # Botones de acción
                btn_col1, btn_col2 = st.columns([3, 1])
                if btn_col1.button("👁️ Ver publicación", key=f"ver_{ruta['id']}", use_container_width=True):
                    st.session_state['modo_perfil'] = 'publicacion'
                    st.session_state['ruta_ver_publicacion'] = ruta
                    st.rerun()
                
                if btn_col2.button("🗑️", key=f"del_{ruta['id']}", use_container_width=True):
                    if profile_service.delete_route(ruta['id'], user_id):
                        st.rerun()