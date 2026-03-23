import streamlit as st
from presentacion import login_view, register_view

st.set_page_config(page_title="Plan&Go Log In", page_icon="🗺️")

def main():
    # 1. Inicializamos las variables de sesión si es la primera vez que entramos
    if 'usuario_logueado' not in st.session_state:
        st.session_state['usuario_logueado'] = None
        
    if 'pantalla_actual' not in st.session_state:
        st.session_state['pantalla_actual'] = "Iniciar Sesión"

    # 2. Lógica de navegación principal
    if st.session_state['usuario_logueado'] is None:
        
        # EL ROUTER: Mira la variable y decide qué pantalla dibujar
        if st.session_state['pantalla_actual'] == "Iniciar Sesión":
            login_view.render()
            
        elif st.session_state['pantalla_actual'] == "Registrarse":
            register_view.render()
            
    # 3. Pantalla de Bienvenida (cuando ya estamos logueados)
    else:
        usuario_actual = st.session_state['usuario_logueado']['username']
        st.title(f"🏠 Bienvenido a Plan&Go, {usuario_actual}!")
        st.write("¡Has iniciado sesión correctamente!")
        
        if st.button("Cerrar Sesión"):
            # Al salir, borramos el usuario y le decimos que vuelva al Login
            st.session_state['usuario_logueado'] = None
            st.session_state['pantalla_actual'] = "Iniciar Sesión" 
            st.rerun()

if __name__ == "__main__":
    main()