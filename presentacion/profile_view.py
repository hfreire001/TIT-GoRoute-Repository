# presentacion/vistas/profile_view.py
import streamlit as st
from negocio import profile_service

def render_profile(user_id):
    # Inyectamos CSS para forzar tamaños y formas
    st.markdown("""
        <style>
            .avatar-container img {
                border-radius: 50%;
                width: 150px !important;
                height: 150px !important;
                object-fit: cover;
                border: 2px solid #ddd;
            }
            .route-thumbnail img {
                width: 100% !important;
                height: 180px !important;
                object-fit: cover;
                border-radius: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    user = profile_service.get_full_profile(user_id)
    if not user:
        st.error("Usuario no encontrado.")
        return

    # --- Cabecera ---
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown('<div class="avatar-container">', unsafe_allow_html=True)
        st.image(user["foto"])
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.title(user["username"])
        c1, c2, c3 = st.columns(3)
        c1.metric("Seguidores", user["seguidores"])
        c2.metric("Seguidos", user["seguidos"])
        c3.metric("Rutas", len(user["rutas"]))
        st.write(f"**Bio:** {user['bio']}")

    st.divider()

    # --- Grid de Rutas ---
    st.subheader("📍 Mis Rutas")
    if not user["rutas"]:
        st.info("No hay rutas que mostrar.")
    else:
        cols = st.columns(3)
        for i, ruta in enumerate(user["rutas"]):
            with cols[i % 3]:
                # Contenedor con clase para tamaño fijo
                st.markdown('<div class="route-thumbnail">', unsafe_allow_html=True)
                st.image(ruta["miniatura"])
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.write(f"**{ruta['nombre']}**")
                
                # Botones de acción
                btn_col1, btn_col2 = st.columns([1, 1])
                with btn_col1:
                    if st.button("Ver", key=f"v_{ruta['id']}", use_container_width=True):
                        st.session_state.current_route = ruta['id']
                
                with btn_col2:
                    # Botón eliminar con confirmación simple
                    if st.button("🗑️", key=f"d_{ruta['id']}", use_container_width=True, help="Eliminar ruta"):
                        if profile_service.delete_route(ruta['id'], user_id):
                            st.success("Ruta eliminada")
                            st.rerun() # Refrescamos para que desaparezca
                        else:
                            st.error("Error al borrar")