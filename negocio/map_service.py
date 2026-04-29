import requests
from datos import route_repo
#API KEY real de OpenRouteService
ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImRhZGI4N2E1YWY0MjRhODQ4NjFkNjFkZmZjMWM2YmM2IiwiaCI6Im11cm11cjY0In0=" 

def calcular_ruta_puntos(coordenadas):
    """
    Calcula la ruta pasando por múltiples puntos (mínimo 2).
    Recibe: [[lon1, lat1], [lon2, lat2], ...]
    """
    url = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"
    
    headers = {
        'Accept': 'application/json, application/geo+json',
        'Authorization': ORS_API_KEY,
        'Content-Type': 'application/json; charset=utf-8'
    }
    
    body = {"coordinates": coordenadas}

    try:
        response = requests.post(url, json=body, headers=headers)
        if response.status_code == 200:
            data = response.json()
            geometria = data['features'][0]['geometry']
            propiedades = data['features'][0]['properties']['summary']
            return True, {
                "geometria": geometria, 
                "distancia_km": propiedades['distance'] / 1000, 
                "duracion_min": propiedades['duration'] / 60
            }
        return False, f"Error API: {response.text}"
    except Exception as e:
        return False, f"Error conexión: {e}"

def obtener_nombre_lugar(lat, lon):
    """Obtiene el nombre del establecimiento usando OpenStreetMap."""
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
    headers = {'User-Agent': 'PlanAndGo_App'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            addr = data.get('address', {})
            # Prioridad: Negocio > Turismo > Nombre general > Calle
            for tag in ['amenity', 'shop', 'tourism', 'leisure', 'historic', 'building']:
                if tag in addr: return addr[tag]
            return data.get('name', addr.get('road', 'Punto seleccionado'))
        return "Punto seleccionado"
    except:
        return "Punto seleccionado"

def publicar_o_clonar_ruta(usuario_actual_id, route_id_original, username, nombre_ruta, descripcion, geometria_geojson, imagen_file, tags_seleccionados, waypoints):
    
    # 1. Le preguntamos a la Base de Datos quién es el dueño original
    creador_original_id = None
    if route_id_original is not None:
        creador_original_id = route_repo.get_creador_ruta(route_id_original)
        
    # 2. Si no hay dueño (ruta desde cero) o NO soy el dueño -> CLONAR (Crear nueva)
    if creador_original_id is None or usuario_actual_id != creador_original_id:
        print("Clonando ruta: No soy el dueño original. Creando copia en mi perfil...")
        return route_repo.guardar_ruta(
            user_id=usuario_actual_id, 
            username=username, 
            nombre_ruta=nombre_ruta, 
            descripcion=descripcion, 
            geometria_geojson=geometria_geojson, 
            imagen_file=imagen_file, 
            tags_seleccionados=tags_seleccionados, 
            waypoints=waypoints
        )
    else:
        # 3. Si YO soy el dueño original de la ruta -> ACTUALIZAR (Sobreescribir)
        print("Actualizando ruta: Soy el dueño de esta ruta. Sobreescribiendo...")
        return route_repo.actualizar_ruta(
            route_id=route_id_original, 
            nombre_ruta=nombre_ruta, 
            descripcion=descripcion, 
            geometria_geojson=geometria_geojson, 
            imagen_file=imagen_file, 
            tags_seleccionados=tags_seleccionados, 
            user_id=usuario_actual_id, 
            waypoints=waypoints
        )