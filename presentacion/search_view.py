import streamlit as st
import json
from negocio import search_service
from presentacion.profile_view import get_image_base64

def load_tags():
    try:
        with open("tags.json", "r", encoding="utf-8") as f:
            # CAMBIADO DE "etiquetas" A "tags" SEGÚN TU JSON
            return json.load(f)["tags"]
    except Exception as e:
        st.error(f"Error al cargar tags.json: {e}")
        return []

def render_search():
    st.title("Explorar 🔍")

    tags_totales = load_tags()

    if "mis_tags_seleccionados" not in st.session_state:
        st.session_state.mis_tags_seleccionados = []

    # --- LÍMITE FÍSICO DE 5 ---
    # Si ya hay 5, solo mostramos las seleccionadas para que no pueda añadir más
    opciones_visibles = tags_totales
    if len(st.session_state.mis_tags_seleccionados) >= 5:
        opciones_visibles = st.session_state.mis_tags_seleccionados
        st.info("📍 Has alcanzado el límite de 5 etiquetas.")

    # Multiselect reactivo (Sin botón de buscar)
    seleccion = st.multiselect(
        "Busca por etiquetas (Máximo 5):",
        options=opciones_visibles,
        default=st.session_state.mis_tags_seleccionados
    )

    # Si hay cambios, actualizamos estado y recargamos para buscar
    if seleccion != st.session_state.mis_tags_seleccionados:
        st.session_state.mis_tags_seleccionados = seleccion
        st.rerun()

    st.divider()

    # BÚSQUEDA AUTOMÁTICA
    estado, rutas = search_service.get_explore_logic(st.session_state.mis_tags_seleccionados)

    if st.session_state.mis_tags_seleccionados:
        if estado == "no_exacto_pero_sugerencias":
            st.warning("⚠️ No hay rutas con todas esas etiquetas.")
        elif estado == "nada":
            st.error("❌ No hay rutas con esas etiquetas.")
            st.subheader("🔥 Te recomendamos estas populares:")
    else:
        st.subheader("🔥 Tendencias")

    # GRID DE MINIATURAS (Sin HTML para evitar errores de visualización)
    if rutas:
        for i in range(0, len(rutas), 3):
            cols = st.columns(3)
            batch = rutas[i:i+3]
            for index, r in enumerate(batch):
                with cols[index]:
                    img_data = get_image_base64(r.get("miniatura"))
                    if img_data:
                        st.image(img_data, use_container_width=True)
                    else:
                        st.markdown("<div style='aspect-ratio:1/1; background:#262730; border-radius:8px;'></div>", unsafe_allow_html=True)
                    
                    st.markdown(f"<p style='text-align:center; font-weight:bold;'>{r['nombre']}</p>", unsafe_allow_html=True)
    else:
        st.info("No hay rutas disponibles.")