import streamlit as st
import folium
from streamlit_folium import st_folium
from negocio import map_service
from datos import route_repo
from streamlit_sortables import sort_items
import colorsys

def formatear_tiempo(total_minutos):
    total_minutos = int(total_minutos)
    dias = total_minutos // 1440           
    horas = (total_minutos % 1440) // 60   
    minutos = total_minutos % 60           
    
    texto = []
    if dias > 0: texto.append(f"{dias} d")
    if horas > 0: texto.append(f"{horas} h")
    if minutos > 0 or (dias == 0 and horas == 0): texto.append(f"{minutos} min")
        
    return " ".join(texto)

def generar_color_hex(indice):
    hue = (indice * 77) % 360 
    r, g, b = colorsys.hls_to_rgb(hue / 360.0, 0.5, 0.9)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

def render():
    st.title("🚶‍♂️ Creador de Rutas a Pie")
    st.write("Añade paradas, organízalas a tu gusto y pulsa 'Calcular' cuando lo tengas claro.")

    if 'puntos_ruta' not in st.session_state:
        st.session_state['puntos_ruta'] = []
    if 'ruta_calculada' not in st.session_state:
        st.session_state['ruta_calculada'] = None
    if 'contador_ubicaciones' not in st.session_state:
        st.session_state['contador_ubicaciones'] = 0

    col_mapa, col_panel = st.columns([2.5, 1.5])

    # ==========================================
    # ZONA IZQUIERDA: EL MAPA
    # ==========================================
    with col_mapa:
        if st.session_state['puntos_ruta']:
            ultimo_punto = st.session_state['puntos_ruta'][-1]
            centro_mapa = [ultimo_punto['lat'], ultimo_punto['lng']]
            zoom_inicial = 14
        else:
            centro_mapa = [40.4168, -3.7038] # Madrid
            zoom_inicial = 6

        m = folium.Map(location=centro_mapa, zoom_start=zoom_inicial)

        for i, punto in enumerate(st.session_state['puntos_ruta']):
            if i == 0: color_hex = "#28a745"
            elif i == len(st.session_state['puntos_ruta']) - 1: color_hex = "#dc3545"
            else: color_hex = generar_color_hex(i)
                
            # 🚀 El popup del mapa ahora muestra el nombre real de la calle
            nombre_lugar = punto.get('nombre', f"Ubicación {punto.get('id', '?')}")
                
            folium.CircleMarker(
                location=[punto['lat'], punto['lng']], 
                radius=10,
                color="white",
                weight=2,
                fill=True,
                fill_color=color_hex,
                fill_opacity=1,
                popup=nombre_lugar
            ).add_to(m)

        if st.session_state['ruta_calculada']:
            ruta_data = st.session_state['ruta_calculada']
            coords_ors = ruta_data['geometria']['coordinates']
            coords_folium = [[p[1], p[0]] for p in coords_ors]
            folium.PolyLine(coords_folium, color="#0078D7", weight=5, opacity=0.8).add_to(m)

        mapa_interactivo = st_folium(m, width=600, height=500, returned_objects=["last_clicked"])

        # Capturar clics 
        if mapa_interactivo and mapa_interactivo.get("last_clicked"):
            clic_actual = mapa_interactivo["last_clicked"]
            
            if not st.session_state['puntos_ruta'] or (st.session_state['puntos_ruta'][-1]['lat'] != clic_actual['lat']):
                st.session_state['contador_ubicaciones'] += 1
                clic_actual['id'] = st.session_state['contador_ubicaciones']
                
                # 🚀 BUSCAMOS EL NOMBRE DEL SITIO ANTES DE GUARDARLO
                with st.spinner("📍 Buscando nombre del lugar..."):
                    nombre = map_service.obtener_nombre_lugar(clic_actual['lat'], clic_actual['lng'])
                    clic_actual['nombre'] = nombre
                
                st.session_state['puntos_ruta'].append(clic_actual)
                st.session_state['ruta_calculada'] = None 
                st.rerun()

    # ==========================================
    # ZONA DERECHA: PANEL DE CONTROL
    # ==========================================
    with col_panel:
        st.subheader("📍 Paradas:")
        
        if not st.session_state['puntos_ruta']:
            st.info("Haz clic en el mapa para empezar.")
        else:
            st.caption("Mantén pulsado y arrastra para cambiar el orden:")
            
            estilo_css = """
            .sortable-item {
                color: white !important;
                border-radius: 8px !important;
                padding: 10px 15px !important;
                margin-bottom: 8px !important;
                font-weight: bold !important;
                font-family: sans-serif !important;
                border: none !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
                cursor: grab !important;
            }
            .sortable-item:active { cursor: grabbing !important; }
            """
            
            nombres_puntos = []
            diccionario_puntos = {}
            
            for i, p in enumerate(st.session_state['puntos_ruta']):
                if i == 0: bg_color = "#28a745"
                elif i == len(st.session_state['puntos_ruta']) - 1: bg_color = "#dc3545"
                else: bg_color = generar_color_hex(i)
                
                estilo_css += f".sortable-item:nth-child({i+1}) {{ background-color: {bg_color} !important; }}\n"
                
                # 🚀 LA ETIQUETA AHORA MUESTRA EL NOMBRE DE LA CALLE (y su ID por si hay calles repetidas)
                nombre_real = p.get('nombre', f"Ubicación {p['id']}")
                nombre_etiqueta = f"{nombre_real} (Id:{p['id']})"
                
                nombres_puntos.append(nombre_etiqueta)
                diccionario_puntos[nombre_etiqueta] = p

            puntos_reordenados = sort_items(nombres_puntos, custom_style=estilo_css)

            if puntos_reordenados and puntos_reordenados != nombres_puntos:
                st.session_state['puntos_ruta'] = [diccionario_puntos[nombre] for nombre in puntos_reordenados]
                
                if len(st.session_state['puntos_ruta']) >= 2:
                    coordenadas_api = [[pt['lng'], pt['lat']] for pt in st.session_state['puntos_ruta']]
                    exito, resultado = map_service.calcular_ruta_puntos(coordenadas_api)
                    if exito: st.session_state['ruta_calculada'] = resultado
                else:
                    st.session_state['ruta_calculada'] = None
                st.rerun() 

            st.write("---")
            
            punto_a_borrar = st.selectbox("¿Borrar una parada?", ["(Elegir parada...)"] + nombres_puntos, label_visibility="collapsed")
            if st.button("❌ Borrar parada seleccionada", use_container_width=True):
                if punto_a_borrar != "(Elegir parada...)":
                    st.session_state['puntos_ruta'].remove(diccionario_puntos[punto_a_borrar])
                    if len(st.session_state['puntos_ruta']) >= 2:
                        coordenadas_api = [[pt['lng'], pt['lat']] for pt in st.session_state['puntos_ruta']]
                        exito, resultado = map_service.calcular_ruta_puntos(coordenadas_api)
                        if exito: st.session_state['ruta_calculada'] = resultado
                    else: st.session_state['ruta_calculada'] = None
                    st.rerun()

        st.write("---")
        
        if len(st.session_state['puntos_ruta']) >= 2:
            if st.button("🚗 Calcular Ruta", type="primary", use_container_width=True):
                with st.spinner("Trazando ruta..."):
                    coordenadas_api = [[p['lng'], p['lat']] for p in st.session_state['puntos_ruta']]
                    exito, resultado = map_service.calcular_ruta_puntos(coordenadas_api)
                    
                    if exito: st.session_state['ruta_calculada'] = resultado; st.rerun()
                    else: st.error(resultado)

        if st.button("🗑️ Borrar todo", use_container_width=True):
            st.session_state['puntos_ruta'] = []
            st.session_state['ruta_calculada'] = None
            st.session_state['contador_ubicaciones'] = 0
            st.rerun()

        # ==========================================
        # RESULTADOS Y GUARDADO
        # ==========================================
        if st.session_state['ruta_calculada']:
            st.success(f"**🚶 Distancia:** {st.session_state['ruta_calculada']['distancia_km']:.1f} km")
            st.success(f"**⏱️ Tiempo:** {formatear_tiempo(st.session_state['ruta_calculada']['duracion_min'])} andando.")
            
            st.write("---")
            st.subheader("💾 Guardar Ruta")
            nombre_ruta = st.text_input("Ponle un nombre a tu ruta:")
            
            if st.button("Guardar en mi perfil", type="primary"):
                if st.session_state.get('usuario_logueado'):
                    user_id = st.session_state['usuario_logueado']['id']
                    exito_guardar = route_repo.guardar_ruta(user_id, nombre_ruta, st.session_state['ruta_calculada']['geometria'])
                    if exito_guardar: st.success("✅ ¡Ruta guardada en PostGIS correctamente!")
                    else: st.error("Hubo un error al guardar.")
                else:
                    st.warning("⚠️ Debes iniciar sesión para poder guardar rutas.")