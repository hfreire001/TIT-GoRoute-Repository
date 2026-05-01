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
    
    
    
    # --- 1. LÓGICA DE NAVEGACIÓN (JERARQUÍA PRIORITARIA) ---
    
    # PRIORIDAD 1: Si hay un perfil ajeno seleccionado, lo mostramos (venga de donde venga)
    if st.session_state.get('perfil_a_ver'):
        render_perfil_ajeno(st.session_state['perfil_a_ver'])
        return

    # PRIORIDAD 2: Si el usuario seleccionó una ruta para ver detalle
    if st.session_state.get('ver_ruta_detalle'):
        if st.button("⬅️ Volver al buscador"):
            st.session_state.ver_ruta_detalle = None
            st.rerun()
        
        ruta_completa = home_service.obtener_ruta_por_id(st.session_state.ver_ruta_detalle, usuario['id'])
        
        if ruta_completa:
            from presentacion.home_view import render_publication
            # Aquí render_publication ya tiene el botón para ir al perfil que configuramos antes
            render_publication(ruta_completa, usuario)
        else:
            st.error("No se pudo cargar la información de la ruta.")
        return

    # --- 2. ESTILOS CSS ---
    st.markdown("""
        <style>
        .container-ruta {
            position: relative;
            cursor: pointer;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        .overlay-stats {
            position: absolute;
            top: 0; bottom: 0; left: 0; right: 0;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s ease;
            font-size: 1.1em;
            gap: 10px;
        }
        .container-ruta:hover .overlay-stats {
            opacity: 1;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- 3. INTERFAZ DEL BUSCADOR (ESTADO NORMAL) ---
    st.title("Explorar 🔍")
    tab_rutas, tab_usuarios = st.tabs(["📍 Buscar Rutas", "👤 Buscar Usuarios"])

    with tab_rutas:
        render_seccion_rutas()

    with tab_usuarios:
        render_seccion_usuarios()
    
    
def render_seccion_usuarios():
    st.subheader("Encuentra a otros usuarios")
    
    # El buscador
    query_user = st.text_input(
        "Buscar por nombre de usuario:", 
        placeholder="Escribe un nombre...",
        key="input_busqueda_usuarios"
    )

    if query_user:
        # Llamada al servicio
        usuarios = search_service.buscar_usuarios(query_user)
        
        if usuarios:
            st.write(f"Resultados para '{query_user}':")
            for u in usuarios:
                # Contenedor para cada usuario
                with st.container():
                    col_img, col_txt, col_btn = st.columns([1, 3, 1.5])
                    
                    with col_img:
                        # Gestión de imagen
                        img_data = get_image_base64(u.get("foto"))
                        src = f"data:image/png;base64,{img_data}" if img_data else "https://www.w3schools.com/howto/img_avatar.png"
                        st.markdown(
                            f'<img src="{src}" style="width:60px; height:60px; border-radius:50%; object-fit:cover; border: 2px solid #4CAF50;">', 
                            unsafe_allow_html=True
                        )
                    
                    with col_txt:
                        # Mostramos el nombre asegurándonos de que no sea None
                        nombre = u.get('username', 'Usuario desconocido')
                        st.markdown(f"**@{nombre}**")
                        
                        bio = u.get('bio') or "Sin biografía"
                        st.caption(f"{bio[:50]}..." if len(bio) > 50 else bio)
                    
                    with col_btn:
                        # Botón que conecta con tu lógica de navegación de render_search
                        if st.button("Ver Perfil", key=f"btn_u_{u['id']}", use_container_width=True):
                            st.session_state['perfil_a_ver'] = u['id']
                            st.rerun()
                    st.divider()
        else:
            st.warning(f"No se han encontrado resultados para '{query_user}'.")
    else:
        st.info("Escribe el nombre de un usuario para ver su actividad.")
        
    
def render_seccion_rutas():
    tags_totales = load_tags()

    if "mis_tags_seleccionados" not in st.session_state:
        st.session_state.mis_tags_seleccionados = []

    # --- Lógica de Multiselect ---
    opciones_visibles = tags_totales
    if len(st.session_state.mis_tags_seleccionados) >= 5:
        opciones_visibles = st.session_state.mis_tags_seleccionados
        st.info("📍 Has alcanzado el límite de 5 etiquetas.")

    seleccion = st.multiselect(
        "Busca por etiquetas (Máximo 5):",
        options=opciones_visibles,
        default=st.session_state.mis_tags_seleccionados
    )

    if seleccion != st.session_state.mis_tags_seleccionados:
        st.session_state.mis_tags_seleccionados = seleccion
        st.rerun()

    st.divider()

    # Obtención de datos desde el servicio
    estado, rutas = search_service.get_explore_logic(st.session_state.mis_tags_seleccionados)

    if st.session_state.mis_tags_seleccionados:
        if estado == "no_exacto_pero_sugerencias":
            st.warning("⚠️ No hay rutas con todas esas etiquetas. Sugerencias:")
        elif estado == "nada":
            st.error("❌ Sin resultados. Tendencias actuales:")
    else:
        st.subheader("🔥 Tendencias")

    # --- GRID DE RESULTADOS CORREGIDO ---
    if rutas:
        for i in range(0, len(rutas), 3):
            cols = st.columns(3)
            batch = rutas[i:i+3]
            for index, r in enumerate(batch):
                with cols[index]:
                    # 1. VALIDACIÓN DE IMAGEN (El punto crítico)
                    # Asegúrate de que en tu SQL el campo se llame 'miniatura' o cámbialo aquí
                    img_raw = r.get("miniatura") 
                    img_base64 = get_image_base64(img_raw) if img_raw else None
                    
                    if img_base64:
                        img_src = f"data:image/png;base64,{img_base64}"
                    else:
                        # Imagen de respaldo para que no aparezca el icono de error
                        img_src = "https://via.placeholder.com/400x400.png?text=Ruta+sin+Imagen"

                    # 2. RENDERIZADO HTML
                    st.markdown(f"""
                        <div class="container-ruta">
                            <img src="{img_src}" style="width:100%; aspect-ratio:1/1; object-fit:cover; border-radius:10px;">
                            <div class="overlay-stats">
                                ❤️ {r.get('likes', 0)}  💬 {r.get('comentarios', 0)}  ⭐ {r.get('guardados', 0)}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # 3. INFORMACIÓN Y BOTONES
                    st.markdown(f"**{r['nombre']}**")
                    
                    # Botón de perfil del creador
                    if st.button(f"👤 @{r.get('username', 'usuario')}", key=f"user_grid_{r['id']}_{i}_{index}"):
                        st.session_state['perfil_a_ver'] = r.get('creator_id')
                        st.rerun()
                    
                    # Botón de detalle
                    if st.button("Ver publicación", key=f"btn_det_{r['id']}_{i}_{index}", use_container_width=True):
                        st.session_state.ver_ruta_detalle = r['id']
                        st.rerun()
    else:
        st.info("No hay rutas disponibles.")

def render_perfil_ajeno(user_id):
    """
    Renderiza el perfil ajeno.
    """
    # ... (Mismo código de render_perfil_ajeno que ya tenías)
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

    if st.button("⬅️ Volver al buscador"):
        st.session_state['perfil_a_ver'] = None
        st.rerun()

    col_foto, col_info = st.columns([1, 2.5])
    with col_foto:
        img_data = get_image_base64(user["foto"])
        avatar_src = f"data:image/png;base64,{img_data}" if img_data else "https://www.w3schools.com/howto/img_avatar.png"
        st.markdown(f'<div class="avatar-container"><img src="{avatar_src}" class="avatar-circle"></div>', unsafe_allow_html=True)

    with col_info:
        st.title(user["username"])
        m1, m2, m3 = st.columns(3)
        m1.metric("Seguidores", user.get("seguidores", 0))
        m2.metric("Seguidos", user.get("seguidos", 0))
        m3.metric("Rutas", len(user.get("rutas", [])))
        st.write(f"**Bio:** {user.get('bio', 'Sin biografía.')}")

    st.divider()
    st.subheader(f"📍 Rutas de @{user['username']}")
    
    if not user.get("rutas"):
        st.info("Este usuario aún no ha publicado rutas.")
    else:
        cols = st.columns(3)
        for i, ruta in enumerate(user["rutas"]):
            with cols[i % 3]:
                r_img_data = get_image_base64(ruta["miniatura"])
                r_src = f"data:image/png;base64,{r_img_data}" if r_img_data else "https://via.placeholder.com/300x200"
                
                st.markdown(f'''
                    <div class="route-card">
                        <div class="img-container">
                            <img src="{r_src}" class="route-img-fixed">
                            <div class="overlay">
                                <div class="stat-item"><span>❤️</span><span>{ruta.get('likes', 0)}</span></div>
                                <div class="stat-item"><span>💬</span><span>{ruta.get('comentarios', 0)}</span></div>
                                <div class="stat-item"><span>🔖</span><span>{ruta.get('guardados', 0)}</span></div>
                            </div>
                        </div>
                        <div class="route-title">{ruta["nombre"]}</div>
                    </div>
                ''', unsafe_allow_html=True)
                
                if st.button("Ver publicación", key=f"v_ajeno_pub_{ruta['id']}", use_container_width=True):
                    # 1. Indicamos qué ruta queremos ver en detalle
                    st.session_state['ver_ruta_detalle'] = ruta['id']
                    # 2. Reseteamos 'perfil_a_ver' para que la jerarquía de render_search() 
                    # detecte que ahora queremos ver el detalle y no el perfil.
                    st.session_state['perfil_a_ver'] = None
                    st.rerun()