import streamlit as st
from negocio import home_service, profile_service
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
    # Colores Identidad (Extraídos de tu configuración de Login)
    AZUL_PROFUNDO = "#003366"
    AZUL_ACENTO = "#4a90d9"
    AZUL_SUAVE = "#5a7ab0"
    FONDO_CARD = "#EBF3FB"
    BORDE_LIGHT = "#d0dcee"

    # Control de navegación interna del perfil
    if 'modo_perfil' not in st.session_state:
        st.session_state['modo_perfil'] = 'grid'

    modo = st.session_state['modo_perfil']
    usuario_logueado = st.session_state.get('usuario_logueado')
    es_mi_perfil = usuario_logueado and usuario_logueado['id'] == user_id

    # 1. ESTILOS CSS ACTUALIZADOS (Paleta Azul Profundo)
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
            
            .avatar-container {{ display: flex; justify-content: center; margin-bottom: 20px; }}
            .avatar-circle {{
                width: 150px; height: 150px;
                border-radius: 50%; object-fit: cover;
                border: 4px solid {FONDO_CARD};
                box-shadow: 0 4px 14px rgba(0, 51, 102, 0.15);
            }}
            .route-card {{
                background-color: {FONDO_CARD}; border-radius: 18px;
                padding: 10px; text-align: center; margin-bottom: 12px;
                border: 1px solid {BORDE_LIGHT};
                transition: transform 0.2s;
            }}
            .route-card:hover {{ transform: translateY(-3px); }}
            
            .img-container {{
                position: relative; width: 100%; height: 150px;
                border-radius: 12px; overflow: hidden;
            }}
            .route-img-fixed {{
                width: 100%; height: 100%; object-fit: cover;
            }}
            .overlay {{
                position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0, 51, 102, 0.75); color: white;
                display: flex; justify-content: center; align-items: center;
                gap: 12px; opacity: 0; transition: 0.3s;
            }}
            .img-container:hover .overlay {{ opacity: 1; }}
            .stat-item {{ display: flex; flex-direction: column; font-size: 0.85em; font-weight: 600; }}
            .route-title {{ 
                font-family: 'Plus Jakarta Sans', sans-serif;
                font-weight: 700; color: {AZUL_PROFUNDO}; 
                margin-top: 10px; font-size: 0.80em; 
            }}
            
            /* Ajuste de Tabs Streamlit */
            .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
            .stTabs [data-baseweb="tab"] {{
                background-color: transparent;
                border-radius: 10px 10px 0 0;
                color: {AZUL_SUAVE};
            }}
        </style>
    """, unsafe_allow_html=True)

    # --- 1. INYECTAR CSS DEL FEED ---
    # Esto asegura que al ver la publicación individual, se vea idéntica al Home
    home_view.inject_custom_css()

    # --- 2. MODO PUBLICACIÓN INDIVIDUAL (VISTA TIPO FEED) ---
    if modo == 'publicacion' and 'ruta_ver_publicacion' in st.session_state:
        ruta_p = st.session_state['ruta_ver_publicacion']
        
        # --- SOLUCIÓN PARA ACTUALIZAR LIKES ---
        # 1. Obtenemos la lista REAL de nombres que han dado like ahora mismo
        nombres_likes = home_service.obtener_nombres_likes(ruta_p['id'])
        
        # 2. El número de likes REAL es el tamaño de esa lista
        conteo_real = len(nombres_likes)
        
        # Botón de retorno estilizado
        if st.button("⬅️ Volver al Perfil", key="back_to_profile"):
            st.session_state['modo_perfil'] = 'grid'
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Mapeo de campos para que coincidan con lo que espera home_view.render_publication
        # Aseguramos que los nombres de las llaves sean los correctos
        ruta_para_renderizar = {
            'id': ruta_p['id'],
            'username': usuario_logueado['username'] if usuario_logueado else "Usuario",
            'creator_id': user_id,
            'nombre': ruta_p.get('nombre'),
            'description': ruta_p.get('description') or ruta_p.get('descripcion', 'Sin descripción'),
            'tags': ruta_p.get('tags', []), 
            'imagen_bytes': get_image_base64(ruta_p.get('miniatura')),
            'num_likes': conteo_real,
            'fecha_bonita': ruta_p.get('fecha', 'Reciente')
        }
        
        # LLAMADA A LA FUNCIÓN QUE YA TIENES EN HOME_VIEW
        home_view.render_publication(ruta_para_renderizar, usuario_logueado)
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
        st.markdown(f"<h1 style='color:{AZUL_PROFUNDO}; padding-bottom:0;'>{user['username']}</h1>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("Seguidores", user["seguidores"])
        m2.metric("Seguidos", user["seguidos"])
        m3.metric("Rutas", len(user["rutas"]))
        st.markdown(f"**Bio:** <span style='color:{AZUL_SUAVE};'>{user['bio'] if user['bio'] else 'Sin biografía.'}</span>", unsafe_allow_html=True)

        if es_mi_perfil:
            with st.popover("✏️ Editar Perfil", use_container_width=True):
                st.markdown(f"<h3 style='color:{AZUL_PROFUNDO}; text-align:center;'>Configuración</h3>", unsafe_allow_html=True)
                with st.form("edit_profile_form", border=False):
                    new_username = st.text_input("Usuario", value=user["username"])
                    new_email = st.text_input("Email", value=user.get("email", ""))
                    new_bio = st.text_area("Biografía", value=user["bio"])
                    
                    st.write("---")
                    new_pass = st.text_input("Nueva contraseña", type="password", placeholder="Omitir para mantener")
                    new_img = st.file_uploader("Cambiar foto", type=["png", "jpg", "jpeg"])
                    
                    if st.form_submit_button("Guardar Cambios", type="primary", use_container_width=True):
                        if not new_username or not new_email:
                            st.warning("Campos obligatorios vacíos.")
                        else:
                            success = profile_service.actualizar_perfil_completo(
                                user_id, new_username, new_email, new_bio, new_pass, new_img
                            )
                            if success:
                                st.session_state['usuario_logueado']['username'] = new_username
                                st.success("¡Listo!")
                                st.rerun()
                            else:
                                st.error("Error al actualizar.")

    st.divider()

    # ---- FUNCIÓN AUXILIAR PARA PINTAR CUADRÍCULAS ----
    def pintar_cuadricula(rutas_lista, es_seccion_favoritos=False):
        if not rutas_lista:
            st.info("No hay rutas aquí.")
            return

        cols = st.columns(3)
        for i, ruta in enumerate(rutas_lista):
            with cols[i % 3]:
                r_src = get_image_base64(ruta.get("miniatura")) or "https://via.placeholder.com/300"
                
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
                
                prefijo = "fav" if es_seccion_favoritos else "pub"
                btn_col1, btn_col2 = st.columns([3, 1])
                if btn_col1.button("Ver", key=f"ver_{prefijo}_{ruta['id']}", use_container_width=True):
                    st.session_state['modo_perfil'] = 'publicacion'
                    st.session_state['ruta_ver_publicacion'] = ruta
                    st.rerun()
                
                if not es_seccion_favoritos and es_mi_perfil:
                    if btn_col2.button("🗑️", key=f"del_{prefijo}_{ruta['id']}", use_container_width=True):
                        if profile_service.delete_route(ruta['id'], user_id):
                            st.rerun()

    # RENDERIZADO DE LAS PESTAÑAS
    if es_mi_perfil:
        tab_mis_rutas, tab_favs = st.tabs(["📍 Mis Rutas", "⭐ Favoritos"])
        with tab_mis_rutas: pintar_cuadricula(user["rutas"], False)
        with tab_favs: pintar_cuadricula(profile_service.get_rutas_favoritas(user_id), True)
    else:
        st.markdown(f"<h3 style='color:{AZUL_PROFUNDO};'>📍 Rutas Publicadas</h3>", unsafe_allow_html=True)
        pintar_cuadricula(user["rutas"], False)
        
        
        
        
# ######################################33
# import streamlit as st
# from negocio import profile_service
# from presentacion import home_view
# import base64
# import os

# def get_image_base64(path):
#     """Convierte una imagen en base64 para mostrarla en HTML."""
#     if not path or not os.path.exists(path):
#         return None
#     try:
#         with open(path, "rb") as image_file:
#             encoded = base64.b64encode(image_file.read()).decode()
#             return f"data:image/png;base64,{encoded}"
#     except:
#         return None

# def render_profile(user_id):
#     --- PALETA DE COLORES PROFESIONAL ---
#     AZUL_P = "#003366"      # Profundo (Títulos)
#     AZUL_A = "#4a90d9"      # Acento (Iconos/Métricas)
#     AZUL_S = "#5a7ab0"      # Suave (Texto secundario)
#     AZUL_F = "#EBF3FB"      # Fondo (Cards/Inputs)
#     AZUL_B = "#D0DCEE"      # Bordes
#     BLANCO = "#FFFFFF"

#     if 'modo_perfil' not in st.session_state:
#         st.session_state['modo_perfil'] = 'grid'

#     modo = st.session_state['modo_perfil']
#     usuario_logueado = st.session_state.get('usuario_logueado')
#     es_mi_perfil = usuario_logueado and usuario_logueado['id'] == user_id

#     1. ESTILOS CSS REFORZADOS
#     st.markdown(f"""
#         <style>
#             @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
            
#             /* Métricas de Seguidores/Seguidos */
#             [data-testid="stMetricValue"] {{
#                 color: {AZUL_P} !important;
#                 font-family: 'Plus Jakarta Sans', sans-serif;
#                 font-weight: 700;
#             }}
#             [data-testid="stMetricLabel"] {{
#                 color: {AZUL_S} !important;
#                 font-weight: 600;
#             }}

#             /* Contenedor del Popover de Edición */
#             div[data-testid="stPopover"] > button {{
#                 background-color: {AZUL_F} !important;
#                 border: 1px solid {AZUL_B} !important;
#                 color: {AZUL_P} !important;
#                 font-weight: 600;
#             }}
            
#             /* Estilo de los botones "Ver" y "Borrar" */
#             .stButton > button {{
#                 border-radius: 8px !important;
#                 font-family: 'Plus Jakarta Sans', sans-serif;
#                 font-size: 0.85rem !important;
#             }}
            
#             /* Botón "Ver Publicación" (Azul clarito con borde) */
#             div.stButton > button[key^="ver_"] {{
#                 background-color: {AZUL_F} !important;
#                 color: {AZUL_P} !important;
#                 border: 1px solid {AZUL_B} !important;
#                 transition: all 0.2s;
#             }}
#             div.stButton > button[key^="ver_"]:hover {{
#                 border-color: {AZUL_A} !important;
#                 background-color: #DDEAF8 !important;
#             }}

#             /* Botón "Papelera" (Azul muy clarito con borde) */
#             div.stButton > button[key^="del_"] {{
#                 background-color: #F8FAFD !important;
#                 border: 1px solid {AZUL_B} !important;
#                 color: {AZUL_S} !important;
#             }}

#             .avatar-circle {{
#                 width: 150px; height: 150px;
#                 border-radius: 50%; object-fit: cover;
#                 border: 4px solid {AZUL_F};
#                 box-shadow: 0 4px 14px rgba(0, 51, 102, 0.1);
#             }}

#             .route-card {{
#                 background-color: {AZUL_F}; border-radius: 18px;
#                 padding: 10px; text-align: center; margin-bottom: 12px;
#                 border: 1px solid {AZUL_B};
#             }}
#         </style>
#     """, unsafe_allow_html=True)

#     2. MODO PUBLICACIÓN (Sin cambios en lógica)
#     if modo == 'publicacion' and 'ruta_ver_publicacion' in st.session_state:
#         ... (se mantiene el código previo de render_publication)
#         pass

#     3. MODO CUADRÍCULA
#     user = profile_service.get_full_profile(user_id)
#     if not user: return

#     col_f, col_i = st.columns([1, 2])
#     with col_f:
#         avatar_src = get_image_base64(user["foto"]) or "https://www.w3schools.com/howto/img_avatar.png"
#         st.markdown(f'<div style="text-align:center;"><img src="{avatar_src}" class="avatar-circle"></div>', unsafe_allow_html=True)
    
#     with col_i:
#         st.markdown(f"<h1 style='color:{AZUL_P}; margin-bottom:10px;'>{user['username']}</h1>", unsafe_allow_html=True)
#         m1, m2, m3 = st.columns(3)
#         m1.metric("Seguidores", user["seguidores"])
#         m2.metric("Seguidos", user["seguidos"])
#         m3.metric("Rutas", len(user["rutas"]))
#         st.markdown(f"<p style='color:{AZUL_S};'><b>Bio:</b> {user['bio'] or 'Sin biografía.'}</p>", unsafe_allow_html=True)

#         if es_mi_perfil:
#             Popover con estilo reforzado
#             with st.popover("✏️ Ajustes de Perfil", use_container_width=True):
#                 st.markdown(f"<div style='background-color:{AZUL_F}; padding:15px; border-radius:12px; border:1px solid {AZUL_B};'>", unsafe_allow_html=True)
#                 with st.form("edit_profile_form", border=False):
#                     st.markdown(f"<h4 style='color:{AZUL_P};'>Editar Información</h4>", unsafe_allow_html=True)
#                     new_username = st.text_input("Usuario", value=user["username"])
#                     new_email = st.text_input("Email", value=user.get("email", ""))
#                     new_bio = st.text_area("Biografía", value=user["bio"])
#                     new_pass = st.text_input("Cambiar contraseña", type="password")
#                     new_img = st.file_uploader("Foto de perfil", type=["png", "jpg"])
                    
#                     if st.form_submit_button("Guardar Cambios", type="primary", use_container_width=True):
#                         Lógica de guardado...
#                         pass
#                 st.markdown("</div>", unsafe_allow_html=True)

#     st.divider()

#     def pintar_cuadricula(rutas_lista, es_fav=False):
#         if not rutas_lista:
#             st.info("No hay rutas.")
#             return

#         cols = st.columns(3)
#         for i, ruta in enumerate(rutas_lista):
#             with cols[i % 3]:
#                 r_src = get_image_base64(ruta.get("miniatura")) or "https://via.placeholder.com/300"
#                 st.markdown(f'''
#                     <div class="route-card">
#                         <img src="{r_src}" style="width:100%; height:120px; object-fit:cover; border-radius:10px;">
#                         <div style="font-family:'Plus Jakarta Sans'; font-weight:700; color:{AZUL_P}; margin:8px 0;">{ruta.get('nombre')}</div>
#                     </div>
#                 ''', unsafe_allow_html=True)
                
                
#                 prefijo = "fav" if es_fav else "pub"
#                 b1, b2 = st.columns([3, 1])
#                 Botones con las clases CSS definidas arriba
#                 if b1.button("Ver", key=f"ver_{prefijo}_{ruta['id']}", use_container_width=True):
#                     st.session_state['modo_perfil'] = 'publicacion'
#                     st.session_state['ruta_ver_publicacion'] = ruta
#                     st.rerun()
                
#                 if not es_fav and es_mi_perfil:
#                     if b2.button("🗑️", key=f"del_{prefijo}_{ruta['id']}", use_container_width=True):
#                         if profile_service.delete_route(ruta['id'], user_id):
#                             st.rerun()

#     Pestañas
#     if es_mi_perfil:
#         t1, t2 = st.tabs(["📍 Mis Rutas", "⭐ Guardadas"])
#         with t1: pintar_cuadricula(user["rutas"], False)
#         with t2: pintar_cuadricula(profile_service.get_rutas_favoritas(user_id), True)
#     else:
#         pintar_cuadricula(user["rutas"], False)