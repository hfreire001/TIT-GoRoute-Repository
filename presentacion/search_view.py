import streamlit as st
import json
from negocio import search_service, home_service, profile_service
from presentacion.profile_view import get_image_base64

def load_tags():
    try:
        with open("tags.json", "r", encoding="utf-8") as f:
            return json.load(f)["tags"]
    except Exception as e:
        st.error(f"Error al cargar tags.json: {e}")
        return []

def render_search():
    usuario = st.session_state.get('usuario_logueado')

    if not usuario:
        st.warning("Debes iniciar sesión para explorar rutas.")
        return 
    
    # --- PALETA DE COLORES (ADN Plan&Go) ---
    AZUL_P = "#003366"  # Profundo
    AZUL_S = "#5a7ab0"  # Suave
    AZUL_F = "#EBF3FB"  # Fondo
    AZUL_B = "#D0DCEE"  # Bordes

    # --- 1. ESTILOS CSS UNIFICADOS (Activa el Hover y Sombras) ---
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');

        .stApp {{ background-color: #FFFFFF; }}

        /* Títulos y textos */
        h1, h2, h3, p, span, label, .stMarkdown, .stCaption {{
            color: {AZUL_P} !important;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }}

        /* Contenedor Principal de la Card (Igual al Perfil) */
        .main-card-container {{
            background-color: {AZUL_F};
            border-radius: 18px;
            padding: 10px;
            border: 1px solid {AZUL_B};
            text-align: center;
            margin-bottom: 15px;
            transition: transform 0.2s ease;
        }}
        .main-card-container:hover {{ transform: translateY(-3px); }}

        /* Wrapper de Imagen y Overlay (Sombreado al pasar el ratón) */
        .img-wrapper {{
            position: relative;
            width: 100%;
            height: 160px;
            border-radius: 12px;
            overflow: hidden;
        }}
        .route-img-fixed {{
            width: 100%; height: 100%; object-fit: cover;
        }}

        /* Overlay que contiene Likes, Comentarios, etc. */
        .overlay {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 51, 102, 0.85); 
            color: white;
            display: flex; justify-content: center; align-items: center;
            gap: 15px; opacity: 0; transition: 0.3s ease;
        }}
        .img-wrapper:hover .overlay {{ opacity: 1; }}
        
        .stat-item {{ 
            display: flex; flex-direction: column; align-items: center; 
            font-size: 0.80rem; font-weight: 600; 
        }}
        .stat-item span {{ color: white !important; }}

        .route-title-style {{
            font-weight: 700; color: {AZUL_P}; 
            margin-top: 10px; font-size: 0.80rem; line-height: 1.1;
        }}

        /* Inputs y Selectores */
        div[data-baseweb="select"], .stTextInput > div > div > input {{
            background-color: white !important;
            border: 2px solid {AZUL_P} !important;
            border-radius: 10px !important;
            
        
        }}
        </style>
    """, unsafe_allow_html=True)
    
    # --- 2. LÓGICA DE NAVEGACIÓN ---
    if st.session_state.get('perfil_a_ver'):
        render_perfil_ajeno(st.session_state['perfil_a_ver'])
        return

    if st.session_state.get('ver_ruta_detalle'):
        if st.button("⬅️ Volver al buscador"):
            st.session_state.ver_ruta_detalle = None
            st.rerun()
        
        ruta_completa = home_service.obtener_ruta_por_id(st.session_state.ver_ruta_detalle, usuario['id'])
        if ruta_completa:
            from presentacion.home_view import render_publication
            render_publication(ruta_completa, usuario)
        return

    # --- 3. INTERFAZ ---
    st.title("Explorar 🔍")
    tab_rutas, tab_usuarios = st.tabs(["📍 Buscar Rutas", "👤 Buscar Usuarios"])

    with tab_rutas:
        render_seccion_rutas()

    with tab_usuarios:
        render_seccion_usuarios()

def render_seccion_rutas():
    tags_totales = load_tags()
    if "mis_tags_seleccionados" not in st.session_state:
        st.session_state.mis_tags_seleccionados = []

    st.subheader("Filtrar por categoría")
    seleccion = st.multiselect("Etiquetas:", options=tags_totales, default=st.session_state.mis_tags_seleccionados)

    if seleccion != st.session_state.mis_tags_seleccionados:
        st.session_state.mis_tags_seleccionados = seleccion
        st.rerun()

    estado, rutas = search_service.get_explore_logic(st.session_state.mis_tags_seleccionados)

    if rutas:
        for i in range(0, len(rutas), 3):
            cols = st.columns(3)
            batch = rutas[i:i+3]
            for index, r in enumerate(batch):
                with cols[index]:
                    img_raw = r.get("miniatura") 
                    img_base64 = get_image_base64(img_raw) if img_raw else None
                    img_src = f"data:image/png;base64,{img_base64}" if img_base64 else "https://via.placeholder.com/300x200"

                    # HTML unificado con profile_view para activar el Hover
                    st.markdown(f'''
                        <div class="main-card-container">
                            <div class="img-wrapper">
                                <img src="{img_src}" class="route-img-fixed">
                                <div class="overlay">
                                    <div class="stat-item"><span>❤️</span><span>{r.get('likes', 0)}</span></div>
                                    <div class="stat-item"><span>💬</span><span>{r.get('comentarios', 0)}</span></div>
                                    <div class="stat-item"><span>⭐</span><span>{r.get('guardados', 0)}</span></div>
                                </div>
                            </div>
                            <div class="route-title-style">{r["nombre"]}</div>
                        </div>
                    ''', unsafe_allow_html=True)
                    
                    # Botones de acción
                    # 2. Botones de acción (Ajustamos proporciones a 2:1 para dar más espacio al nombre)
                    # 2. Botones de acción (Proporción optimizada para nombres largos)
                    st.markdown("""
                        <style>
                            /* Selecciona los párrafos (p) dentro de CUALQUIER botón en CUALQUIER columna */
                            div[data-testid="stColumn"] button p {
                                font-size: 0.8rem !important;
                                white-space: nowrap;
                            }
                        </style>
                    """, unsafe_allow_html=True)

                    # 2. Tu grid de rutas
                    c1, c2 = st.columns([2.2, 0.8]) 

                    with c1:
                        nombre_usuario = r.get('username', 'usuario')
                        if st.button(f"👤@{nombre_usuario}", key=f"u_{r['id']}_{i}_{index}", use_container_width=True):
                            st.session_state['perfil_a_ver'] = r.get('creator_id')
                            st.rerun()

                    with c2:
                        if st.button("Ver", key=f"btn_v_{r['id']}_{i}_{index}", use_container_width=True):
                            st.session_state.ver_ruta_detalle = r['id']
                            st.rerun()
                            
    else:
        st.info("No hay rutas que coincidan con la búsqueda.")

def render_seccion_usuarios():
    query_user = st.text_input("Buscar por nombre:", placeholder="Escribe un nombre...", key="input_busqueda_usuarios")

    if query_user:
        usuarios = search_service.buscar_usuarios(query_user)
        if usuarios:
            for u in usuarios:
                with st.container():
                    col_img, col_txt, col_btn = st.columns([0.6, 3, 1.2])
                    img_data = get_image_base64(u.get("foto"))
                    src = f"data:image/png;base64,{img_data}" if img_data else "https://www.w3schools.com/howto/img_avatar.png"
                    
                    with col_img:
                        st.markdown(f'<img src="{src}" style="width:50px; height:50px; border-radius:50%; object-fit:cover; border: 2px solid #003366;">', unsafe_allow_html=True)
                    with col_txt:
                        st.markdown(f"<b>@{u.get('username')}</b><br><small>{u.get('bio')[:40] if u.get('bio') else ''}...</small>", unsafe_allow_html=True)
                    with col_btn:
                        if st.button("Perfil", key=f"btn_u_search_{u['id']}", use_container_width=True):
                            st.session_state['perfil_a_ver'] = u['id']
                            st.rerun()
                st.markdown("---")

                
                
def render_perfil_ajeno(user_id):
    """
    Renderiza el perfil ajeno con UI circular y botones estilizados.
    """
    # --- PALETA DE COLORES ---
    AZUL_P = "#003366"  # Profundo
    AZUL_S = "#5a7ab0"  # Suave
    AZUL_F = "#EBF3FB"  # Fondo
    AZUL_B = "#D0DCEE"  # Bordes

    # 1. ESTILOS CSS CONSOLIDADOS (Avatar Circular + Botones + Cards)
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
            
            /* --- AVATAR CIRCULAR REFORZADO --- */
            .avatar-container {{
                display: flex;
                justify-content: center;
                align-items: center;
                margin-bottom: 20px;
            }}
            .avatar-circle {{
                width: 150px !important;
                height: 150px !important;
                border-radius: 50% !important;
                object-fit: cover !important;
                border: 4px solid {AZUL_F};
                box-shadow: 0 4px 14px rgba(0, 51, 102, 0.15);
            }}

            /* --- BOTONES DE SEGUIMIENTO --- */
            /* Botón Seguir (Primary) */
            div.stButton > button[kind="primary"] {{
                background-color: {AZUL_P} !important;
                color: #FFFFFF !important;
                border: none !important;
                font-weight: 700 !important;
                padding: 0.5rem 1rem !important;
            }}
            div.stButton > button[kind="primary"] p {{
                color: white !important;
                font-size: 1rem !important;
            }}

            /* Botón Dejar de seguir (Secondary) */
            div.stButton > button[kind="secondary"] {{
                background-color: transparent !important;
                color: {AZUL_P} !important;
                border: 2px solid {AZUL_P} !important;
                font-weight: 600 !important;
            }}
            div.stButton > button[kind="secondary"] p {{
                color: {AZUL_P} !important;
            }}

            /* --- TARJETAS DE RUTAS (Main Card) --- */
            .main-card-container {{
                background-color: {AZUL_F};
                border-radius: 18px;
                padding: 10px;
                border: 1px solid {AZUL_B};
                text-align: center;
                margin-bottom: 15px;
                transition: transform 0.2s ease;
            }}
            .main-card-container:hover {{ transform: translateY(-3px); }}

            .img-wrapper {{
                position: relative;
                width: 100%;
                height: 140px;
                border-radius: 12px;
                overflow: hidden;
            }}
            .route-img-fixed {{
                width: 100%; height: 100%; object-fit: cover;
            }}
            .overlay {{
                position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0, 51, 102, 0.85); color: white;
                display: flex; justify-content: center; align-items: center;
                gap: 15px; opacity: 0; transition: 0.3s ease;
            }}
            .img-wrapper:hover .overlay {{ opacity: 1; }}
            
            .stat-item {{ display: flex; flex-direction: column; align-items: center; font-size: 0.8rem; font-weight: 600; }}
            .stat-item span {{ color: white !important; }}

            .route-title-style {{
                font-family: 'Plus Jakarta Sans', sans-serif; 
                font-weight: 700; color: {AZUL_P}; 
                margin-top: 10px; font-size: 0.85rem; line-height: 1.1;
            }}
        </style>
    """, unsafe_allow_html=True)

    user = profile_service.get_full_profile(user_id)
    if not user:
        st.error("No se pudo cargar el perfil.")
        return

    if st.button("⬅️ Volver al buscador"):
        st.session_state['perfil_a_ver'] = None
        st.rerun()

    # Cabecera del Perfil
    col_foto, col_info = st.columns([1, 2.5])
    with col_foto:
        img_data = get_image_base64(user["foto"])
        avatar_src = f"data:image/png;base64,{img_data}" if img_data else "https://www.w3schools.com/howto/img_avatar.png"
        st.markdown(f'<div class="avatar-container"><img src="{avatar_src}" class="avatar-circle"></div>', unsafe_allow_html=True)

    with col_info:
        st.markdown(f"<h1 style='color:{AZUL_P}; margin-bottom:5px;'>{user['username']}</h1>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("Seguidores", user.get("seguidores", 0))
        m2.metric("Seguidos", user.get("seguidos", 0))
        m3.metric("Rutas", len(user.get("rutas", [])))
        st.markdown(f"<p style='color:{AZUL_P};'><b>Bio:</b> {user.get('bio', 'Sin biografía.')}</p>", unsafe_allow_html=True)

        # --- GESTIÓN DE SEGUIMIENTO ---
        usuario_logueado = st.session_state.get('usuario_logueado')
        if usuario_logueado and usuario_logueado['id'] != user_id:
            ya_le_sigue = profile_service.verificar_seguimiento(usuario_logueado['id'], user_id)
            
            if not ya_le_sigue:
                if st.button("➕ Seguir", type="primary", use_container_width=True):
                    profile_service.gestionar_seguimiento(usuario_logueado['id'], user_id, False)
                    st.rerun()
            else:
                if st.button("Dejar de seguir", type="secondary", use_container_width=True):
                    profile_service.gestionar_seguimiento(usuario_logueado['id'], user_id, True)
                    st.rerun()

    st.divider()
    st.markdown(f"<h3 style='color:{AZUL_P};'>📍 Rutas de @{user['username']}</h3>", unsafe_allow_html=True)
    
    if not user.get("rutas"):
        st.info("Este usuario aún no ha publicado rutas.")
    else:
        # Rejilla de rutas del usuario ajeno
        cols_rutas = st.columns(3)
        for i, ruta in enumerate(user["rutas"]):
            with cols_rutas[i % 3]:
                r_img_data = get_image_base64(ruta["miniatura"])
                r_src = f"data:image/png;base64,{r_img_data}" if r_img_data else "https://via.placeholder.com/300x200"
                
                st.markdown(f'''
                    <div class="main-card-container">
                        <div class="img-wrapper">
                            <img src="{r_src}" class="route-img-fixed">
                            <div class="overlay">
                                <div class="stat-item"><span>❤️</span><span>{ruta.get('likes', 0)}</span></div>
                                <div class="stat-item"><span>💬</span><span>{ruta.get('comentarios', 0)}</span></div>
                                <div class="stat-item"><span>⭐</span><span>{ruta.get('guardados', 0)}</span></div>
                            </div>
                        </div>
                        <div class="route-title-style">{ruta["nombre"]}</div>
                    </div>
                ''', unsafe_allow_html=True)
                
                if st.button("Ver publicación", key=f"v_ajeno_pub_{ruta['id']}", use_container_width=True):
                    st.session_state['ver_ruta_detalle'] = ruta['id']
                    st.session_state['perfil_a_ver'] = None
                    st.rerun()