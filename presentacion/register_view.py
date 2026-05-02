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
                # 1. Registramos al usuario (con los paréntesis en lower() que corregimos)
                exito, mensaje = auth_service.registrar_usuario(username_input.lower(), email_input.lower(), password_input)
                
                if exito:
                    # 🚀 SOLUCIÓN: Hacemos "auto-login" para traer todos los datos (incluido el ID)
                    login_exito, datos_usuario = auth_service.verificar_login(username_input.lower(), password_input)
                    
                    if login_exito:
                        # Usamos toast para que el mensaje sobreviva al rerun
                        st.toast("✅ ¡Cuenta creada! Entrando automáticamente...", icon="🚀")
                        
                        # Guardamos el usuario con su ID real y forzamos recarga
                        st.session_state['usuario_logueado'] = datos_usuario
                        st.session_state['pagina_actual'] = "🏠 Feed"
                        st.rerun() 
                else:
                    st.error(mensaje)
            else:
                st.warning("⚠️ Por favor, rellena todos los campos.")
                
    # --- BOTÓN PARA VOLVER ---
    st.write("") 
    st.markdown("---") 
    
    if st.button("⬅️ Volver a Iniciar Sesión"):
        # Importante: En tu app.py lo llamamos "Login", no "Iniciar Sesión"
        st.session_state['pantalla_actual'] = "Login"
        st.rerun()