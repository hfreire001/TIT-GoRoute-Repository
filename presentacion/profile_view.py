# presentacion/vistas/profile_view.py
import streamlit as st
from negocio import profile_service
import base64
import os

def get_image_base64(path):
    """ Convierte una imagen local a base64 para mostrarla en HTML sin restricciones de Streamlit. """
    if path and os.path.exists(path):
        try:
            with open(path, "rb") as f:
                data = f.read()
            # Detectar extensión para el tipo MIME
            ext = path.split('.')[-1].lower()
            return f"data:image/{ext};base64,{base64.b64encode(data).decode()}"
        except Exception:
            return None
    return None

def render_profile(user_id):
    # 1. CSS REFORZADO (Garantiza círculo y tamaños fijos)
    st.markdown("""
        <style>
            /* Contenedor y estilo del Avatar Circular */
            .avatar-container {
                display: flex;
                justify-content: center;
                margin-bottom: 20px;
            }
            .avatar-circle {
                width: 160px !important;
                height: 160px !important;
                border-radius: 50% !important;
                object-fit: cover !important;
                border: 4px solid #4CAF50;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
            }

            /* Estilo de las Tarjetas de Ruta */
            .route-card {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                padding: 10px;
                text-align: center;
                margin-bottom: 15px;
            }
            .route-img-fixed {
                width: 100% !important;
                height: 180px !important;
                object-fit: cover !important;
                border-radius: 10px !important;
                margin-bottom: 8px;
            }
            .route-title {
                font-weight: bold;
                font-size: 1.1em;
                margin-bottom: 10px;
                color: #FFFFFF;
            }
        </style>
    """, unsafe_allow_html=True)

    # 2. CARGA DE DATOS
    user = profile_service.get_full_profile(user_id)
    if not user:
        st.error(f"No se pudo cargar el perfil para el ID: {user_id}")
        return

    # 3. CABECERA DEL PERFIL (Avatar + Información)
    col_foto, col_info = st.columns([1, 2.5])

    with col_foto:
        img_data = get_image_base64(user["foto"])
        # Si no hay imagen física, usamos un placeholder
        avatar_src = img_data if img_data else "https://www.w3schools.com/howto/img_avatar.png"
        
        st.markdown(
            f'<div class="avatar-container">'
            f'<img src="{avatar_src}" class="avatar-circle">'
            f'</div>', 
            unsafe_allow_html=True
        )

    with col_info:
        st.title(user["username"])
        
        # Métricas (Seguidores, Seguidos, Rutas)
        m1, m2, m3 = st.columns(3)
        m1.metric("Seguidores", user["seguidores"])
        m2.metric("Seguidos", user["seguidos"])
        m3.metric("Rutas", len(user["rutas"]))
        
        st.write(f"**Bio:** {user['bio'] if user['bio'] else 'Este aventurero aún no tiene biografía.'}")
        
        if st.button("✏️ Editar Perfil", use_container_width=True):
            st.info("Funcionalidad de edición próximamente.")

    st.divider()

    # 4. CUADRÍCULA DE RUTAS
    st.subheader("📍 Mis Rutas Publicadas")
    
    if not user["rutas"]:
        st.info("No hay rutas creadas todavía.")
    else:
        # Generar grid de 3 columnas
        cols = st.columns(3)
        for i, ruta in enumerate(user["rutas"]):
            with cols[i % 3]:
                # Preparar imagen de la ruta en Base64
                r_img_data = get_image_base64(ruta["miniatura"])
                r_src = r_img_data if r_img_data else "https://via.placeholder.com/300x200?text=Sin+Imagen"
                
                # Renderizar tarjeta de ruta con HTML
                st.markdown(
                    f'<div class="route-card">'
                    f'<img src="{r_src}" class="route-img-fixed">'
                    f'<div class="route-title">{ruta["nombre"]}</div>'
                    f'</div>', 
                    unsafe_allow_html=True
                )
                
                # Botones de Acción (Usamos columnas pequeñas para los botones)
                c1, c2 = st.columns([3, 1])
                with c1:
                    if st.button("Explorar", key=f"v_{ruta['id']}", use_container_width=True):
                        st.session_state.current_route = ruta['id']
                        st.success(f"Cargando {ruta['nombre']}...")
                with c2:
                    # Botón de eliminar (Papelera)
                    if st.button("🗑️", key=f"d_{ruta['id']}", use_container_width=True):
                        # Acción: Borrar de DB + Borrar Archivo
                        if profile_service.delete_route(ruta['id'], user_id):
                            st.rerun() # Recarga para actualizar lista y contador
                        else:
                            st.error("Error al borrar")

    # Espaciado final
    st.markdown("<br><br>", unsafe_allow_html=True)