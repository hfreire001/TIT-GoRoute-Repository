import streamlit as st
import json
import base64
import os
from negocio import search_service
from negocio import profile_service

def load_tags():
    try:
        with open("tags.json", "r", encoding="utf-8") as f:
            return json.load(f)["tags"]
    except:
        return []

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

def render_perfil_ajeno(user_id):
    """
    Renderiza el perfil siguiendo la estructura de profile_view 
    pero ELIMINANDO los botones de edición y borrar.
    """
    # CSS idéntico al de tu profile_view
    st.markdown("""
        <style>
            .avatar-container { display: flex; justify-content: center; margin-bottom: 20px; }
            .avatar-circle {
                width: 160px !important; height: 160px !important;
                border-radius: 50% !important; object-fit: cover !important;
                border: 4px solid #4CAF50; box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
            }
            .route-card {
                background-color: #ffffff; border-radius: 15px;
                padding: 10px; text-align: center; margin-bottom: 15px;
                box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
            }
            .img-container {
                position: relative; width: 100%; height: 180px;
                border-radius: 10px; overflow: hidden;
            }
            .route-img-fixed {
                width: 100% !important; height: 100% !important;
                object-fit: cover !important; transition: 0.3s ease;
            }
            .overlay {
                position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0, 0, 0, 0.6); color: white;
                display: flex; justify-content: center; align-items: center;
                gap: 15px; opacity: 0; transition: 0.3s ease;
            }
            .img-container:hover .overlay { opacity: 1; }
            .img-container:hover .route-img-fixed { transform: scale(1.05); }
            .route-title {
                font-weight: bold; font-size: 1.1em;
                color: #000000 !important; margin: 10px 0;
            }
            .stat-item { display: flex; flex-direction: column; align-items: center; font-size: 0.9em; }
        </style>
    """, unsafe_allow_html=True)

    user = profile_service.get_full_profile(user_id)
    if not user:
        st.error("No se pudo cargar el perfil.")
        return

    # Botón para volver atrás
    if st.button("⬅️ Volver al buscador"):
        st.session_state['perfil_a_ver'] = None
        st.rerun()

    # Cabecera (Sin botón editar)
    col_foto, col_info = st.columns([1, 2.5])
    with col_foto:
        img_data = get_image_base64(user["foto"])
        avatar_src = img_data if img_data else "https://www.w3schools.com/howto/img_avatar.png"
        st.markdown(f'<div class="avatar-container"><img src="{avatar_src}" class="avatar-circle"></div>', unsafe_allow_html=True)

    with col_info:
        st.title(user["username"])
        m1, m2, m3 = st.columns(3)
        m1.metric("Seguidores", user["seguidores"])
        m2.metric("Seguidos", user["seguidos"])
        m3.metric("Rutas", len(user["rutas"]))
        st.write(f"**Bio:** {user['bio'] if user['bio'] else 'Sin biografía.'}")
        # AQUÍ YA NO ESTÁ EL BOTÓN DE EDITAR

    st.divider()
    st.subheader(f"📍 Rutas de @{user['username']}")
    
    if not user["rutas"]:
        st.info("Este usuario aún no ha publicado rutas.")
    else:
        cols = st.columns(3)
        for i, ruta in enumerate(user["rutas"]):
            with cols[i % 3]:
                r_img_data = get_image_base64(ruta["miniatura"])
                r_src = r_img_data if r_img_data else "https://via.placeholder.com/300x200"
                
                st.markdown(f'''
                    <div class="route-card">
                        <div class="img-container">
                            <img src="{r_src}" class="route-img-fixed">
                            <div class="overlay">
                                <div class="stat-item"><span>❤️</span><span>{ruta['likes']}</span></div>
                                <div class="stat-item"><span>💬</span><span>{ruta['comentarios']}</span></div>
                                <div class="stat-item"><span>🔖</span><span>{ruta['guardados']}</span></div>
                            </div>
                        </div>
                        <div class="route-title">{ruta["nombre"]}</div>
                    </div>
                ''', unsafe_allow_html=True)
                
                # Solo botón Explorar (Sin botón borrar)
                if st.button("Explorar ruta", key=f"v_ajeno_{ruta['id']}", use_container_width=True):
                    st.session_state['ruta_activa_id'] = ruta['id']
                    st.session_state['modo_mapa'] = 'ver'
                    st.session_state['pagina_actual'] = "📍 Crear ruta"
                    st.rerun()

def render_search():
    # Si hay un ID en 'perfil_a_ver', renderizamos la vista de solo lectura
    if st.session_state.get('perfil_a_ver'):
        render_perfil_ajeno(st.session_state['perfil_a_ver'])
        return

    # Lógica normal del buscador
    st.title("Explorar 🔍")
    tags_totales = load_tags()
    
    if "mis_tags_seleccionados" not in st.session_state:
        st.session_state.mis_tags_seleccionados = []

    opciones = tags_totales if len(st.session_state.mis_tags_seleccionados) < 5 else st.session_state.mis_tags_seleccionados
    seleccion = st.multiselect(
        "Busca por etiquetas (Máximo 5):", 
        options=opciones, 
        default=st.session_state.mis_tags_seleccionados
    )

    if seleccion != st.session_state.mis_tags_seleccionados:
        st.session_state.mis_tags_seleccionados = seleccion
        st.rerun()

    st.divider()
    estado, rutas = search_service.get_explore_logic(st.session_state.mis_tags_seleccionados)

    if rutas:
        for i in range(0, len(rutas), 3):
            cols = st.columns(3)
            batch = rutas[i:i+3]
            for idx, r in enumerate(batch):
                with cols[idx]:
                    img_path = r.get("miniatura")
                    img_data = get_image_base64(img_path)
                    if img_data:
                        st.image(img_data, use_container_width=True)
                    
                    st.markdown(f"**{r['nombre']}**")
                    
                    if st.button(f"@{r.get('username', 'User')}", key=f"u_btn_{r['id']}_{i+idx}"):
                        st.session_state['perfil_a_ver'] = r['creator_id']
                        st.rerun()

                    if st.button("Ver mapa", key=f"m_btn_{r['id']}_{i+idx}", use_container_width=True):
                        st.session_state['ruta_activa_id'] = r['id']
                        st.session_state['modo_mapa'] = 'ver'
                        st.session_state['pagina_actual'] = "📍 Crear ruta"
                        st.rerun()