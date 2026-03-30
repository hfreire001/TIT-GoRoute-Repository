import streamlit as st
from presentacion import map_view

# Configuración de la página (layout="wide" para que el mapa se vea más grande)
st.set_page_config(page_title="Plan&Go - Mapa", page_icon="🗺️", layout="wide")

def main():
    # Como solo el mapa
    map_view.render()

if __name__ == "__main__":
    main()