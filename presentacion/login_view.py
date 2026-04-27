import streamlit as st
from negocio import auth_service

def render():
    st.title("Iniciar Sesión")
    
    with st.form("formulario_login"):
        username_input = st.text_input("Usuario")
        password_input = st.text_input("Contraseña", type="password")
        submit_btn = st.form_submit_button("Entrar")
        
        if submit_btn:
            if username_input and password_input:
                exito, resultado = auth_service.verificar_login(username_input, password_input)
                
                if exito:
                    st.session_state['usuario_logueado'] = resultado
                    st.success("¡Acceso concedido!")
                    st.rerun() 
                else:
                    st.error(resultado)
            else:
                st.warning("⚠️ Por favor, rellena todos los campos.")
                
    st.write("") # Espacio en blanco
    st.markdown("---") # Línea separadora visual
    st.write("¿Aún no tienes cuenta en Plan&Go?")
    
    # Si el usuario pulsa este botón...
    if st.button("Regístrate aquí"):
        # Le decimos a la sesión que cambie a la pantalla de registro
        st.session_state['pantalla_actual'] = "Registrarse"
        st.rerun() # Recargamos la app para que aplique el cambio