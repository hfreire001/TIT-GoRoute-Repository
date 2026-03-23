import requests

# ⚠️ Pon aquí tu API KEY real de OpenRouteService
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