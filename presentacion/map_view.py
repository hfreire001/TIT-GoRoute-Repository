import streamlit as st
import folium
from streamlit_folium import st_folium
from negocio import map_service
from datos import route_repo
from streamlit_sortables import sort_items
import colorsys
import json
import os

def cargar_tags():
    ruta_json = 'tags.json'
    if os.path.exists(ruta_json):
        with open(ruta_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            return datos.get("tags", [])
    else:
        st.error("No se ha encontrado el archivo tags.json en la raíz del proyecto.")
        return []

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
    modo = st.session_state.get('modo_mapa', 'crear')
    ruta_id = st.session_state.get('ruta_activa_id')

    if modo == 'ver' and ruta_id:
        cargar_modo_lectura(ruta_id)
    elif modo == 'editar' and ruta_id:
        if st.session_state.get('editando_route_id') != ruta_id:
            cargar_datos_para_editar(ruta_id)
        render_creador_normal(edit_mode=True)
    else:
        render_creador_normal(edit_mode=False)

def cargar_datos_para_editar(route_id):
    datos_ruta = route_repo.get_route_by_id(route_id)
    if not datos_ruta: return
    
    nombre, desc, geom_json, tags, distancia_m, waypoints_json = datos_ruta
    
    if waypoints_json:
        waypoints = json.loads(waypoints_json) if isinstance(waypoints_json, str) else waypoints_json
        st.session_state['puntos_ruta'] = waypoints
        st.session_state['contador_ubicaciones'] = max([wp.get('id', 0) for wp in waypoints]) if waypoints else 0
    else:
        geom = json.loads(geom_json) 
        coord_inicio = geom['coordinates'][0]
        coord_fin = geom['coordinates'][-1]
        st.session_state['puntos_ruta'] = [
            {"lat": coord_inicio[1], "lng": coord_inicio[0], "id": 1, "nombre": "Inicio original"},
            {"lat": coord_fin[1], "lng": coord_fin[0], "id": 2, "nombre": "Fin original"}
        ]
        st.session_state['contador_ubicaciones'] = 2
    
    st.session_state['edit_nombre'] = nombre
    st.session_state['edit_desc'] = desc if desc else ""
    st.session_state['edit_tags'] = tags if tags else []
    st.session_state['editando_route_id'] = route_id
    
    coordenadas_api = [[pt['lng'], pt['lat']] for pt in st.session_state['puntos_ruta']]
    exito, resultado = map_service.calcular_ruta_puntos(coordenadas_api)
    if exito: st.session_state['ruta_calculada'] = resultado

def cargar_modo_lectura(route_id):
    datos_ruta = route_repo.get_route_by_id(route_id)
    if not datos_ruta:
        st.error("No se pudo cargar la ruta.")
        return

    nombre, desc, geom_json, tags, distancia_m, waypoints_json = datos_ruta
    geom = json.loads(geom_json) 
    distancia_km = (distancia_m / 1000) if distancia_m else 0
    
    st.title(f"📍 Explorando: {nombre}")
    
    if st.button("⬅️ Volver al Perfil"):
        st.session_state['modo_mapa'] = 'crear' 
        st.session_state['ruta_activa_id'] = None
        st.session_state['pagina_actual'] = "👤 Perfil" 
        st.rerun()

    col_mapa, col_info = st.columns([2.5, 1.5])

    with col_mapa:
        primer_punto = geom['coordinates'][0]
        m = folium.Map(location=[primer_punto[1], primer_punto[0]], zoom_start=14)
        
        coords_folium = [[p[1], p[0]] for p in geom['coordinates']]
        folium.PolyLine(coords_folium, color="#0078D7", weight=5).add_to(m)
        
        if waypoints_json:
            waypoints = json.loads(waypoints_json) if isinstance(waypoints_json, str) else waypoints_json
            for i, wp in enumerate(waypoints):
                color_hex = "#28a745" if i == 0 else ("#dc3545" if i == len(waypoints)-1 else generar_color_hex(i))
                folium.CircleMarker(
                    location=[wp['lat'], wp['lng']], 
                    radius=10, color="white", weight=2, fill=True, fill_color=color_hex, fill_opacity=1,
                    tooltip=wp.get('nombre', f'Parada {i}')
                ).add_to(m)
        else:
            folium.CircleMarker(coords_folium[0], radius=10, color="white", weight=2, fill=True, fill_color="#28a745", fill_opacity=1, tooltip="Inicio").add_to(m)
            folium.CircleMarker(coords_folium[-1], radius=10, color="white", weight=2, fill=True, fill_color="#dc3545", fill_opacity=1, tooltip="Fin").add_to(m)
        
        st_folium(m, width=800, height=600, returned_objects=[])

    with col_info:
        st.subheader("Detalles de la ruta")
        st.success(f"**🚶 Distancia:** {distancia_km:.1f} km")
        st.write(f"**Descripción:** {desc if desc else 'Sin descripción.'}")
        if tags:
            etiquetas_html = "".join([f'<span style="background-color:#e1e4e8; color:#0366d6; padding:4px 10px; border-radius:12px; margin-right:5px; margin-bottom:5px; font-size:13px; display:inline-block;">{t}</span>' for t in tags])
            st.markdown(etiquetas_html, unsafe_allow_html=True)
        st.divider()
        st.info("💡 Ruta calculada para realizarse a pie.")

def render_creador_normal(edit_mode=False):
    if edit_mode:
        st.title("✏️ Editando tu ruta")
        if st.button("❌ Cancelar edición"):
            st.session_state['modo_mapa'] = 'crear'
            st.session_state['editando_route_id'] = None
            st.session_state['puntos_ruta'] = []
            st.session_state['ruta_calculada'] = None
            st.session_state['pagina_actual'] = "👤 Perfil"
            st.rerun()
    else:
        st.title("📍 Creador de Rutas")

    if 'puntos_ruta' not in st.session_state:
        st.session_state['puntos_ruta'] = []
    if 'ruta_calculada' not in st.session_state:
        st.session_state['ruta_calculada'] = None
    if 'contador_ubicaciones' not in st.session_state:
        st.session_state['contador_ubicaciones'] = 0

    col_mapa, col_panel = st.columns([2.5, 1.5]) 

    with col_mapa:
        if st.session_state['puntos_ruta']:
            ultimo_punto = st.session_state['puntos_ruta'][-1]
            centro_mapa = [ultimo_punto['lat'], ultimo_punto['lng']]
            zoom_inicial = 14
        else:
            centro_mapa = [43.2630, -2.9350] # Bilbao
            zoom_inicial = 12

        m = folium.Map(location=centro_mapa, zoom_start=zoom_inicial)

        for i, punto in enumerate(st.session_state['puntos_ruta']):
            color_hex = "#28a745" if i == 0 else ("#dc3545" if i == len(st.session_state['puntos_ruta'])-1 else generar_color_hex(i))
            folium.CircleMarker(
                location=[punto['lat'], punto['lng']], 
                radius=10, color="white", weight=2, fill=True, fill_color=color_hex, fill_opacity=1,
                popup=punto.get('nombre', 'Parada')
            ).add_to(m)

        if st.session_state['ruta_calculada']:
            coords_ors = st.session_state['ruta_calculada']['geometria']['coordinates']
            coords_folium = [[p[1], p[0]] for p in coords_ors] 
            folium.PolyLine(coords_folium, color="#0078D7", weight=5, opacity=0.8).add_to(m)

        mapa_interactivo = st_folium(m, width=800, height=600, returned_objects=["last_clicked"])

        if mapa_interactivo and mapa_interactivo.get("last_clicked"):
            clic = mapa_interactivo["last_clicked"]
            if not st.session_state['puntos_ruta'] or (st.session_state['puntos_ruta'][-1]['lat'] != clic['lat']):
                st.session_state['contador_ubicaciones'] += 1
                clic['id'] = st.session_state['contador_ubicaciones'] 
                with st.spinner("Buscando lugar..."):
                    clic['nombre'] = map_service.obtener_nombre_lugar(clic['lat'], clic['lng'])
                st.session_state['puntos_ruta'].append(clic)
                st.session_state['ruta_calculada'] = None
                st.rerun()

    with col_panel:
        st.subheader("Paradas:")
        if not st.session_state['puntos_ruta']:
            st.info("Haz clic en el mapa.")
        else:
            st.caption("Mantén pulsado y arrastra para cambiar el orden:")
            
            # 🚀 AQUÍ ESTÁ EL CÓDIGO CSS RESTAURADO PARA LOS COLORES 🚀
            estilo_css = """
            .sortable-item {
                color: white !important; border-radius: 8px !important;
                padding: 10px 15px !important; margin-bottom: 8px !important;
                font-weight: bold !important; font-family: sans-serif !important;
                border: none !important; box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
                cursor: grab !important;
            }
            .sortable-item:active { cursor: grabbing !important; }
            """
            
            nombres_puntos = []
            diccionario_puntos = {}
            
            for i, p in enumerate(st.session_state['puntos_ruta']):
                # Generamos el mismo color exacto que el pin del mapa
                color_bg = "#28a745" if i == 0 else ("#dc3545" if i == len(st.session_state['puntos_ruta'])-1 else generar_color_hex(i))
                estilo_css += f".sortable-item:nth-child({i+1}) {{ background-color: {color_bg} !important; }}\n"
                
                nombre_etiqueta = f"{p.get('nombre', 'Ubicación')} (Id:{p['id']})"
                nombres_puntos.append(nombre_etiqueta)
                diccionario_puntos[nombre_etiqueta] = p

            # Le pasamos el custom_style a la lista
            puntos_reordenados = sort_items(nombres_puntos, custom_style=estilo_css)
            
            if puntos_reordenados and puntos_reordenados != nombres_puntos:
                st.session_state['puntos_ruta'] = [diccionario_puntos[n] for n in puntos_reordenados]
                st.rerun() 

            st.write("---")
            
            # Selector y botón para borrar una sola parada
            punto_a_borrar = st.selectbox("¿Borrar una parada?", ["(Elegir parada...)"] + nombres_puntos, label_visibility="collapsed")
            if st.button("Borrar parada seleccionada", use_container_width=True):
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
                if st.button("Calcular Ruta", type="primary", use_container_width=True):
                    with st.spinner("Trazando ruta..."):
                        coordenadas_api = [[p['lng'], p['lat']] for p in st.session_state['puntos_ruta']]
                        exito, resultado = map_service.calcular_ruta_puntos(coordenadas_api)
                        if exito: st.session_state['ruta_calculada'] = resultado; st.rerun()
                        else: st.error(resultado)

            if st.button("Borrar todo", use_container_width=True):
                st.session_state['puntos_ruta'] = []
                st.session_state['ruta_calculada'] = None
                st.session_state['contador_ubicaciones'] = 0
                st.rerun()

    if st.session_state['ruta_calculada']:
        st.success(f"**🚶 Distancia:** {st.session_state['ruta_calculada']['distancia_km']:.1f} km")
        st.success(f"**⏱️ Tiempo:** {formatear_tiempo(st.session_state['ruta_calculada']['duracion_min'])} andando.")
        
        st.write("---")
        st.subheader("Guardar Cambios" if edit_mode else "Publicar Ruta")
        
        def_nombre = st.session_state.get('edit_nombre', "") if edit_mode else ""
        def_desc = st.session_state.get('edit_desc', "") if edit_mode else ""
        def_tags = st.session_state.get('edit_tags', []) if edit_mode else []
        
        nombre_ruta = st.text_input("Nombre:", value=def_nombre)
        opciones_tags = cargar_tags()
        tags_sel = st.multiselect("Etiquetas:", options=opciones_tags, default=[t for t in def_tags if t in opciones_tags])
        desc_ruta = st.text_area("Descripción:", value=def_desc)
        imagen_ruta = st.file_uploader("Foto:", type=["jpg", "png"])
        
        if st.button("Guardar" if not edit_mode else "Actualizar", type="primary"):
            uid = st.session_state['usuario_logueado']['id']
            username = st.session_state['usuario_logueado']['username']
            
            # Llamamos directamente al Cerebro pasándole el ID de la ruta que estamos viendo
            exito = map_service.publicar_o_clonar_ruta(
                usuario_actual_id=uid,
                route_id_original=st.session_state.get('ruta_activa_id'),
                username=username,
                nombre_ruta=nombre_ruta,
                descripcion=desc_ruta,
                geometria_geojson=st.session_state['ruta_calculada']['geometria'],
                imagen_file=imagen_ruta,
                tags_seleccionados=tags_sel,
                waypoints=st.session_state['puntos_ruta']
            )
            
            if exito: 
                st.success("¡Ruta guardada y procesada correctamente en tu perfil!")
                st.balloons()
            else: 
                st.error("Hubo un error al procesar la ruta.")