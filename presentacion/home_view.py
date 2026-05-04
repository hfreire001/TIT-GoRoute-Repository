# presentacion/home_view.py
import streamlit as st
from negocio import home_service

def inject_custom_css():
    """
    Inyecta estilos CSS avanzados basados exclusivamente en la paleta de colores del login.
    Define colores globales, estilos de tarjetas limpias y modernas.
    """
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        /* --- PALETA DE COLORES GLOBAL (sampled de login.png) --- */
        :root {
            /* Azules Principales */
            --primary-blue: #0059B2;    /* El azul del botón 'Entrar' */
            --primary-hover: #00468C;  /* Azul más oscuro para hover de botones sólidos */
            
            /* Fondos */
            --page-bg: #EBF3FB;         /* AZUL TENUE DE FONDO (sampled de whitespace login) */
            --card-bg: #A5C1E6;         /* NUEVO: Celeste para el fondo de cada publicación */
            
            /* Bordes y Sombras */
            --card-border: #D0DCEE;     /* AZUL TENUE BORDES (como inputs login) */
            --divider-color: #E2E8F0;   /* Separador gris muy tenue */
            --card-shadow: 0 4px 12px rgba(15, 23, 42, 0.05); /* Sombra suave para tarjetas */

            /* Textos */
            --text-title: #003366;      /* Azul oscuro títulos principals */
            --text-subtitle: #5A7AB0;   /* Gris-azulado secundario (como subtítulo login) */
            --text-body: #334155;       /* Texto de cuerpo */
            --text-secondary: #64748B;  /* Gris secundario para captions */
            
            /* Inputs */
            --input-border: #D0DCEE;    /* Borde input reposo */
            --input-text: #1A2D4A;      /* Texto de inputs */
            --input-shadow-focus: rgba(0, 89, 178, 0.15); /* Sombra azul en focus */
        }

        /* --- ESTILOS TIPOGRÁFICOS GLOBALES --- */
        .stApp, .stApp p, .stApp label {
            font-family: 'Inter', sans-serif !important;
            color: var(--text-body);
        }
        .stApp h1, .stApp h2, .stApp h3 {
            font-family: 'Inter', sans-serif !important;
            color: var(--text-title) !important;
            font-weight: 700 !important;
        }
        .stApp h1 { font-size: 2.2rem !important; margin-bottom: 0.5rem !important; }
        .stApp h3 { font-size: 1.3rem !important; margin-bottom: 0.8rem !important; }

        /* --- CONTENEDOR DE LA VISTA COMPLETA (Fondo AZUL TENUE) --- */
        /* Intentamos aplicar el fondo claro a toda la vista */
        .stAppViewMain {
            background-color: var(--page-bg);
        }

        /* --- TARJETA DE PUBLICACIÓN PROPIA (rounded corners, white bg, shadow, blue border) --- */
        /* Eliminamos el borde native de Streamlit y lo reemplazamos con nuestra envoltura limpia */
        .clean-feed-card {
            background-color: var(--card-bg) !important;
            border-radius: 12px !important;
            box-shadow: var(--card-shadow) !important;
            border: 1px solid var(--card-border) !important; /* Borde azul tenue */
            padding: 20px !important;
            margin-bottom: 30px !important;
        }

        /* --- SEPARADOR (st.divider) modernizado --- */
        hr {
            border-top: 1px solid var(--divider-color) !important; /* Separador gris muy tenue */
            margin-top: 20px !important;
            margin-bottom: 20px !important;
        }

        /* --- BOTÓN DE USUARIO COMO ENLACE (Modernizado Gris-Azulado) --- */
        .stButton > button[key^="user_link_"] {
            border: none;
            background: transparent;
            color: var(--text-subtitle); /* Gris-azulado por defecto */
            padding: 0;
            font-weight: 600;
            font-size: 1.1em;
            text-align: left;
            transition: color 0.2s;
        }
        .stButton > button[key^="user_link_"]:hover {
            color: var(--primary-blue) !important; /* Azul sólido en hover */
            text-decoration: none !important;
            background: transparent !important;
        }

        /* --- IMÁGENES DE RUTA (Bordes redondeados) --- */
        [data-testid="stImage"] img {
            border-radius: 8px !important;
        }

        /* --- TAGS (Limpios y Grises-Azulados) --- */
        .route-tag {
            font-size: 0.8em;
            color: var(--text-subtitle);
            font-weight: normal;
            margin-left: 8px;
            padding: 2px 6px;
            background-color: #F1F5F9; /* Fondo gris suave */
            border-radius: 4px;
        }

        /* --- ELIMINAR GLITCHES DE POPOVERS Y EXPANDERS NATIVOS --- */
        /* Dejamos de targetear los internals. Solo targeteamos las columnas contenedoras
           para aplicar colores secundarios a los textos. */

        /* Usaremos envolturas div únicas para targetear estas columnas de forma segura */
        .interaction-col div div div p { color: var(--text-subtitle) !important; }
        .comments-expander-wrapper details summary { color: var(--text-title) !important; font-weight: 600 !important; }
        .comments-expander-wrapper details p { color: var(--text-body) !important; }

        /* --- CAMPOS DE ENTRADA (Inputs como login, borde azul tenue) --- */
        [data-testid="stWidgetInputTextInput"] input, [data-testid="stForm"] input {
            border-radius: 8px !important;
            border: 1px solid var(--input-border) !important; /* Borde azul tenue reposo */
            background-color: #FFFFFF !important;
            color: var(--input-text) !important;
            padding: 0.6rem 0.8rem !important;
        }
        [data-testid="stWidgetInputTextInput"] input:focus, [data-testid="stForm"] input:focus {
            border-color: var(--primary-blue) !important; /* Azul sólido en focus */
            box-shadow: 0 0 0 2px var(--input-shadow-focus) !important;
        }
        [data-testid="stWidgetInputTextInput"] input::placeholder, [data-testid="stForm"] input::placeholder {
            color: var(--text-subtitle) !important; /* Gris-azulado placeholder */
        }

        /* --- BOTONES DE ACCIÓN PRINCIPALES (AZULES SÓLIDOS como Entrar) --- */
        /* Targeteamos los botones de Mapa para que sean solid blue */
        button[key^="ver_map_"], button[key^="mod_map_"], button[key^="submit_comm_"] {
            background-color: var(--primary-blue) !important;
            color: #FFFFFF !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            border: none !important;
            padding: 0.6rem 1rem !important;
            transition: background 0.2s;
        }
        button[key^="ver_map_"]:hover, button[key^="mod_map_"]:hover, button[key^="submit_comm_"]:hover {
            background-color: var(--primary-hover) !important;
        }

        </style>
    """, unsafe_allow_html=True)

def render_publication(ruta, usuario_logueado):
    """
    Renderiza una única publicación envolviéndola en una envoltura de tarjeta limpia y azul.
    """
    # 1. Envolvemos todo en nuestro div de tarjeta limpia PROPIO
    st.markdown('<div class="clean-feed-card">', unsafe_allow_html=True)

    # Contenido de la publicación sin border nativo de Streamlit
    with st.container():
        # 1. Cabecera: Nombre de usuario y Fecha
        col_u, col_f = st.columns([3, 1])
        
        with col_u:
            nombre_user = ruta.get('username', 'Usuario')
            id_creador = ruta.get('creator_id') 
            
            if st.button(f"@{nombre_user}", key=f"user_link_{ruta['id']}"):
                if id_creador:
                    st.session_state['perfil_a_ver'] = id_creador
                    st.session_state['pagina_actual'] = "🔍 Explorar"
                    st.rerun()
                else:
                    st.warning("No se pudo obtener el ID de este usuario.")
        
        with col_f:
            st.markdown(f"<p style='text-align: right; color: var(--text-subtitle);'>{ruta.get('fecha_bonita', 'Reciente')}</p>", unsafe_allow_html=True)
        
        # 2. Imagen de la ruta
        try:
            if ruta.get('imagen_bytes'):
                st.image(ruta['imagen_bytes'], use_container_width=True)
            else:
                st.image("https://images.unsplash.com/photo-1506197603052-3cc9c3a201bd?q=80&w=1000", use_container_width=True)
        except Exception:
            st.error("No se pudo cargar la imagen.")
        
        # 3. Título y Etiquetas (Tags - HTML modernizado)
        etiquetas_crudas = ruta.get('tags') 
        tags_html = ""
        
        if etiquetas_crudas and isinstance(etiquetas_crudas, list):
            tags_format = " ".join([f"#{t.strip()}" for t in etiquetas_crudas if t.strip()])
            tags_html = f"<span class='route-tag'>{tags_format}</span>"
        
        titulo = ruta.get('nombre') or ruta.get('name') or "Sin nombre"
        st.markdown(f"<h3>{titulo} {tags_html}</h3>", unsafe_allow_html=True)
        
        # 4. Descripción
        if ruta.get('description') or ruta.get('descripcion'):
            desc = ruta.get('description') or ruta.get('descripcion')
            st.write(desc)
        
        st.divider()

        # 5. Interacciones: Likes y Favoritos (Columna wrapper para CSS)
        # Usamos div envolventes únicos para aplicar colores secundarios sin romper componentes nativos
        st.markdown('<div class="interaction-col">', unsafe_allow_html=True)
        col_like, col_fav, col_text_likes = st.columns([1, 1, 8]) 
        
        estado_like, estado_fav = home_service.obtener_estado_interacciones(ruta['id'], usuario_logueado['id'])
        
        with col_like:
            # Likes ahora son AZULES por defecto, rojo solo en hover para semántica
            corazon = "💙" if estado_like else "🤍"
            if st.button(corazon, key=f"like_{ruta['id']}"):
                home_service.gestionar_like(usuario_logueado['id'], ruta['id'], estado_like)
                st.rerun()
        
        with col_fav:
            # Estrella amarilla por semántica idiomática de favs
            estrella = "⭐" if estado_fav else "☆"
            if st.button(estrella, key=f"fav_{ruta['id']}"):
                home_service.gestionar_favorito(usuario_logueado['id'], ruta['id'], estado_fav)
                st.rerun()
                
        with col_text_likes:
            num_likes = ruta.get('num_likes', 0)
            # Texto gris-azulado como en login
            with st.popover(f"{num_likes} Me gusta", use_container_width=False):
                usuarios_like = home_service.obtener_nombres_likes(ruta['id'])
                if usuarios_like:
                    for u in usuarios_like:
                        st.markdown(f"👤 **@{u['username']}**")
                else:
                    st.caption("Aún no hay likes.")
        st.markdown('</div>', unsafe_allow_html=True)

        # 6. Sección de Comentarios (Expander modernizado Tono Azul)
        st.markdown('<div class="comments-expander-wrapper">', unsafe_allow_html=True)
        with st.expander("💬 Comentarios"):
            comentarios = home_service.obtener_comentarios_ruta(ruta['id'])
            if comentarios:
                for c in comentarios:
                    # Texto gris-cuerpo limpio
                    st.markdown(f"<strong>@{c['username']}</strong>: {c['content']}", unsafe_allow_html=True)
            else:
                st.caption("No hay comentarios todavía.")
            
            st.write("") 
            
            # Formulario de comentario (Inputs modernizados)
            with st.form(key=f"form_comm_{ruta['id']}", clear_on_submit=True, border=False):
                col_input, col_btn = st.columns([4, 1])
                with col_input:
                    # Input limpio con placeholders en gris-azulado
                    nuevo_comentario = st.text_input("Añade un comentario...", label_visibility="collapsed", placeholder="Tu comentario...")
                with col_btn:
                    # Botón azul como el de 'Entrar'
                    submit_btn = st.form_submit_button("Enviar", use_container_width=True, key=f"submit_comm_{ruta['id']}")
                    
                if submit_btn and nuevo_comentario.strip():
                    home_service.publicar_comentario(usuario_logueado['id'], ruta['id'], nuevo_comentario)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # 7. Botones de Mapa (Ver/Modificar - Azules como login)
        st.divider()
        col_ver, col_mod = st.columns(2)
        
        with col_ver:
            if st.button("🗺️ Ver en Mapa", use_container_width=True, key=f"ver_map_{ruta['id']}"):
                st.session_state['modo_mapa'] = 'ver'
                st.session_state['ruta_activa_id'] = ruta['id']
                st.session_state['pagina_actual'] = "📍 Crear ruta"
                st.rerun()

        with col_mod:
            # El botón SIEMPRE es azul y clicable
            if st.button("🛠️ Modificar Ruta", use_container_width=True, key=f"mod_map_{ruta['id']}"):
                st.session_state['modo_mapa'] = 'editar'
                st.session_state['ruta_activa_id'] = ruta['id']
                st.session_state['pagina_actual'] = "📍 Crear ruta"
                st.rerun()

    # 2. Cerramos nuestro div de tarjeta limpia PROPIO
    st.markdown('</div>', unsafe_allow_html=True)

def render():
    """
    Función principal de la vista Home (Feed).
    Inyecta el CSS azul y renderiza el feed.
    """
    # 1. Inyectamos los estilos personalizados (una sola vez)
    inject_custom_css()

    st.title("Mi Feed")
    # Texto secundario bajo el título en Gris-Azulado
    st.markdown("<p style='color: var(--text-subtitle); margin-top: -15px; margin-bottom: 25px;'>Las últimas rutas de la comunidad que sigues.</p>", unsafe_allow_html=True)

    usuario = st.session_state.get('usuario_logueado')
    
    if not usuario:
        st.error("Error: No se ha iniciado sesión correctamente.")
        return

    # Usamos st.spinner de color primary blue si es posible (Streamlit nativo)
    with st.spinner('Cargando tus rutas...'):
        rutas_feed = home_service.obtener_feed_usuario(usuario['id'])

    if not rutas_feed:
        st.info("Aún no sigues a nadie o tus amigos no han publicado nada.")
    else:
        # Renderizamos cada publicación envolviéndola en nuestra tarjeta limpia y azul
        for ruta in rutas_feed:
            render_publication(ruta, usuario)