import streamlit as st
from negocio import auth_service

def render():
    st.title("Registrar usuario")
    
    with st.form("formulario_registro"):
        email_input = st.text_input("Email")
        username_input = st.text_input("Usuario")
        password_input = st.text_input("Contraseña", type="password")
        submit_btn = st.form_submit_button("Registrarse")
        
        if submit_btn:
            if username_input and email_input and password_input:
                # Llamamos a la capa de negocio
                exito, mensaje = auth_service.registrar_usuario(username_input.lower, email_input.lower, password_input)
                
                if exito:
                    st.success(mensaje)
                    # Le decimos a la sesión quién es y forzamos la recarga
                    st.session_state['usuario_logueado'] = {"username": username_input}
                    st.rerun() 
                    
                else:
                    st.error(mensaje)
            else:
                st.warning("⚠️ Por favor, rellena todos los campos.")
                
    # --- BOTÓN PARA VOLVER ---
    st.write("") 
    st.markdown("---") 
    
    if st.button("⬅️ Volver a Iniciar Sesión"):
        st.session_state['pantalla_actual'] = "Iniciar Sesión"
        st.rerun()