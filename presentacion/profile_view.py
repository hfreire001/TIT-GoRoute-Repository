# presentacion/vistas/profile_view.py
import streamlit as st
from negocio import profile_service

def render_profile(user_id):
    user = profile_service.get_full_profile(user_id)

    if not user:
        st.error("No se pudo cargar el perfil.")
        return

    # Cabecera
    col_img, col_txt = st.columns([1, 2])
    with col_img:
        # Aplicamos un estilo CSS inline para hacer la imagen redonda
        st.markdown(
            f'<img src="{user["foto"]}" style="border-radius: 50%; width: 150px; height: 150px; object-fit: cover; border: 3px solid #00c853;">', 
            unsafe_allow_html=True
        )

    with col_txt:
        st.title(user["username"])
        s1, s2, s3 = st.columns(3)
        s1.metric("Rutas", len(user["rutas"]))
        s2.metric("Seguidores", user["seguidores"])
        s3.metric("Seguidos", user["seguidos"])
        st.info(user["bio"])

    st.divider()
    
    # Grid de Rutas
    st.subheader("📍 Mis Rutas Publicadas")
    cols = st.columns(3)
    for idx, ruta in enumerate(user["rutas"]):
        with cols[idx % 3]:
            st.image(ruta["miniatura"], use_container_width=True)
            st.write(f"**{ruta['nombre']}**")
            if st.button("Ver Ruta", key=f"btn_{ruta['id']}", use_container_width=True):
                st.success(f"Cargando mapa de: {ruta['nombre']}")