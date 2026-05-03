import streamlit as st
from negocio import auth_service

def render():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

            /* ── Fondo general ── */
            .stApp {
                background: linear-gradient(135deg, #e8f0fb 0%, #f0f4ff 50%, #e4edf9 100%);
                min-height: 100vh;
            }

            /* ── Ocultar decoración por defecto de Streamlit ── */
            header[data-testid="stHeader"] {
                background: transparent !important;
                height: 0 !important;
                min-height: 0 !important;
                padding: 0 !important;
                visibility: hidden !important;
            }
            #MainMenu { visibility: hidden !important; }
            footer { visibility: hidden !important; }
            .stDeployButton { display: none !important; }
            .block-container {
                padding-top: 3rem !important;
                padding-bottom: 3rem !important;
            }

            /* ── Fuente global ── */
            html, body, [class*="css"] {
                font-family: 'Plus Jakarta Sans', sans-serif !important;
            }

            /* ── Tarjeta principal ── */
            .login-card {
                background: #EBF3FB;
                border-radius: 24px;
                box-shadow:
                    0 4px 6px rgba(0, 51, 102, 0.04),
                    0 12px 40px rgba(0, 51, 102, 0.10),
                    0 0 0 1px rgba(0, 51, 102, 0.06);
                padding: 2.5rem 2rem 2rem 2rem;
                margin: 0 auto;
            }

            /* ── Cabecera de la tarjeta ── */
            .login-header {
                text-align: center;
                margin-bottom: 0.25rem;
            }
            .login-title {
                color: #003366;
                font-size: 1.6rem;
                font-weight: 700;
                letter-spacing: -0.5px;
                margin: 0.75rem 0 0.25rem 0;
            }
            .login-subtitle {
                color: #5a7ab0;
                font-size: 0.88rem;
                font-weight: 400;
                margin-bottom: 1.5rem;
            }

            /* ── Divisor decorativo ── */
            .divider {
                width: 40px;
                height: 3px;
                background: linear-gradient(90deg, #003366, #4a90d9);
                border-radius: 2px;
                margin: 0 auto 1.75rem auto;
            }

            /* ── Labels de los inputs ── */
            label[data-testid="stWidgetLabel"] p {
                font-family: 'Plus Jakarta Sans', sans-serif !important;
                font-weight: 600 !important;
                font-size: 0.82rem !important;
                color: #003366 !important;
                letter-spacing: 0.3px;
                text-transform: uppercase;
                margin-bottom: 4px !important;
            }

            /* ── Inputs de texto ── */
            input[type="text"],
            input[type="password"] {
                font-family: 'Plus Jakarta Sans', sans-serif !important;
                border: 1.5px solid #d0dcee !important;
                border-radius: 10px !important;
                padding: 0.65rem 0.9rem !important;
                font-size: 0.95rem !important;
                color: #1a2d4a !important;
                background: #f8faff !important;
                transition: border-color 0.2s, box-shadow 0.2s !important;
            }
            input[type="text"]:focus,
            input[type="password"]:focus {
                border-color: #003366 !important;
                box-shadow: 0 0 0 3px rgba(0, 51, 102, 0.10) !important;
                background: #ffffff !important;
            }
            input::placeholder {
                color: #a0b3cc !important;
                font-size: 0.9rem !important;
            }

            /* ── Botón primario (Entrar) ── */
            .stFormSubmitButton > button,
            .stFormSubmitButton > button:focus {
                background: linear-gradient(135deg, #003366 0%, #004f99 100%) !important;
                color: #ffffff !important;
                font-family: 'Plus Jakarta Sans', sans-serif !important;
                font-weight: 600 !important;
                font-size: 0.95rem !important;
                border: none !important;
                border-radius: 12px !important;
                padding: 0.65rem 1rem !important;
                width: 100% !important;
                letter-spacing: 0.3px;
                transition: transform 0.15s, box-shadow 0.15s !important;
                box-shadow: 0 4px 14px rgba(0, 51, 102, 0.28) !important;
                margin-top: 0.5rem !important;
            }
            .stFormSubmitButton > button:hover {
                transform: translateY(-1px) !important;
                box-shadow: 0 6px 20px rgba(0, 51, 102, 0.36) !important;
            }
            .stFormSubmitButton > button:active {
                transform: translateY(0) !important;
            }

            /* ── Botón secundario (Registrarse) ── */
            .stButton > button[kind="secondary"],
            .stButton > button {
                font-family: 'Plus Jakarta Sans', sans-serif !important;
                font-weight: 600 !important;
                font-size: 0.9rem !important;
                color: #003366 !important;
                background: transparent !important;
                border: 1.5px solid #c0d0e8 !important;
                border-radius: 12px !important;
                padding: 0.55rem 1rem !important;
                width: 100% !important;
                transition: background 0.15s, border-color 0.15s !important;
            }
            .stButton > button:hover {
                background: #eef4fb !important;
                border-color: #003366 !important;
            }

            /* ── Texto inferior ── */
            .footer-text {
                text-align: center;
                color: #7a93b5;
                font-size: 0.85rem;
                margin: 1rem 0 0.5rem 0;
            }

            /* ── Alertas ── */
            .stAlert {
                border-radius: 10px !important;
                font-family: 'Plus Jakarta Sans', sans-serif !important;
                font-size: 0.88rem !important;
            }

            /* ── Responsive móvil ── */
            @media (max-width: 640px) {
                .login-card {
                    padding: 2rem 1.25rem 1.5rem 1.25rem !important;
                    border-radius: 18px !important;
                }
                .login-title { font-size: 1.35rem !important; }
                .block-container {
                    padding-left: 0.75rem !important;
                    padding-right: 0.75rem !important;
                }
            }
        </style>
    """, unsafe_allow_html=True)

    # Columnas para centrar en pantallas grandes; en móvil se apilan solas
    col_izq, col_centro, col_der = st.columns([1, 2, 1])

    with col_centro:
        # Tarjeta envolvente
        st.markdown('<div class="login-card">', unsafe_allow_html=True)

        # Logo centrado y con tamaño controlado
        _l, _m, _r = st.columns([1.5, 1, 1.5])
        with _m:
            st.image("assets/logo.png", use_container_width=True)

        # Cabecera
        st.markdown("""
            <div class="login-header">
                <h2 class="login-title">Iniciar Sesión</h2>
                <p class="login-subtitle">¡Bienvenido de nuevo, viajero!</p>
                <div class="divider"></div>
            </div>
        """, unsafe_allow_html=True)

        # Formulario — lógica sin tocar
        with st.form("formulario_login"):
            username_input = st.text_input("Usuario", placeholder="Introduce tu nombre de usuario")
            password_input = st.text_input("Contraseña", type="password", placeholder="••••••••")

            submit_btn = st.form_submit_button("Entrar", use_container_width=True)

            if submit_btn:
                if username_input and password_input:
                    exito, resultado = auth_service.verificar_login(username_input, password_input)
                    if exito:
                        st.session_state['usuario_logueado'] = resultado
                        st.success("¡Acceso concedido!")
                        st.rerun()
                    else:
                        st.error(f"❌ {resultado}")
                else:
                    st.warning("⚠️ Por favor, rellena todos los campos.")

        # Pie de formulario — lógica sin tocar
        st.write("")
        st.markdown("<p class='footer-text'>¿Aún no tienes cuenta en Plan&Go?</p>", unsafe_allow_html=True)

        if st.button("Regístrate aquí", use_container_width=True, type="secondary"):
            st.session_state['pantalla_actual'] = "Registrarse"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)