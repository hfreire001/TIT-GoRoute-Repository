import streamlit as st
from negocio import profile_service
import base64
import os

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

def render_profile(user_id):
    # CSS con efecto Hover y Título Negro
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
            /* Capa sombreada oculta */
            .overlay {
                position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0, 0, 0, 0.6); color: white;
                display: flex; justify-content: center; align-items: center;
                gap: 15px; opacity: 0; transition: 0.3s ease;
            }
            .img-container:hover .overlay { opacity: 1; }
            .img-container:hover .route-img-fixed { transform: scale(1.05); }
            
            /* Título en negro */
            .route-title {
                font-weight: bold; font-size: 1.1em;
                color: #000000 !important; margin: 10px 0;
            }
            .stat-item { display: flex; flex-direction: column; align-items: center; font-size: 0.9em; }
        </style>
    """, unsafe_allow_html=True)

    user = profile_service.get_full_profile(user_id)
    if not user:
        st.error(f"No se pudo cargar el perfil para el ID: {user_id}")
        return

    # Cabecera
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
        st.button("✏️ Editar Perfil", use_container_width=True)

    st.divider()
    st.subheader("📍 Mis Rutas Publicadas")
    
    if not user["rutas"]:
        st.info("No hay rutas creadas todavía.")
    else:
        cols = st.columns(3)
        for i, ruta in enumerate(user["rutas"]):
            with cols[i % 3]:
                r_img_data = get_image_base64(ruta["miniatura"])
                r_src = r_img_data if r_img_data else "https://via.placeholder.com/300x200"
                
                # HTML con Hover e información de likes/comentarios/guardados
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
                
                c1, c2 = st.columns([3, 1])
                with c1:
                    if st.button("Explorar", key=f"v_{ruta['id']}", use_container_width=True):
                        # 1. Cargamos los datos de la ruta para el mapa
                        st.session_state['ruta_activa_id'] = ruta['id']
                        st.session_state['modo_mapa'] = 'ver'
                        
                        # 2. ¡EL SALTO MÁGICO! 
                        # Cambiamos la página actual a la del mapa
                        st.session_state['pagina_actual'] = "📍 Crear ruta"
                        
                        # 3. Forzamos la recarga inmediata
                        st.rerun()
                with c2:
                    if st.button("🗑️", key=f"d_{ruta['id']}", use_container_width=True):
                        if profile_service.delete_route(ruta['id'], user_id):
                            st.rerun()