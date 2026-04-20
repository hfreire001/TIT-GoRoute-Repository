import streamlit as st
# Importamos la vista que hemos creado con el formulario y el límite de 5
from presentacion import search_view 

# 1. Configuración de la página (DEBE SER LO PRIMERO)
st.set_page_config(page_title="PLAN & GO - Explorar", layout="wide")

def main():
    # Estilos globales si quisieras (opcional)
    st.sidebar.title("PLAN & GO 👁️🫦👁️")
    
    # Navegación sencilla (Puedes añadir más vistas aquí luego)
    menu = ["Explorar 🔍", "Perfil", "Mapa"]
    choice = st.sidebar.selectbox("Navegación", menu)

    if choice == "Explorar 🔍":
        # Llamamos a la función render_search() que está en tu carpeta vistas
        search_view.render_search()
    
    elif choice == "Perfil":
        st.write("Aquí iría tu profile_view.render_profile()")
    
    elif choice == "Mapa":
        st.write("Aquí iría tu map_view.render_map()")

if __name__ == "__main__":
    main()