import os
from datos import home_repo

# Tu ruta base del PC
BASE_PATH = r"C:\Users\blbla\Desktop\TIT-GoRoute-Repository-conexion_cambio\TIT-GoRoute-Repository-conexion_cambio"

def procesar_datos_ruta(ruta):
    """
    Función auxiliar para procesar imágenes y fechas de una ruta 
    venga del feed o de una búsqueda individual.
    """
    path_bbdd = ruta.get('thumbnail_url') 
    
    if path_bbdd:
        # Limpiamos y unimos rutas de SO
        path_limpio = os.path.normpath(path_bbdd.lstrip("\\/"))
        path_local = os.path.join(BASE_PATH, path_limpio)
        
        if os.path.exists(path_local):
            with open(path_local, "rb") as f:
                ruta['imagen_bytes'] = f.read()
        else:
            ruta['imagen_bytes'] = "https://images.unsplash.com/photo-1551632811-561732d1e306?q=80&w=1000&auto=format&fit=crop"
    else:
        ruta['imagen_bytes'] = "https://images.unsplash.com/photo-1551632811-561732d1e306?q=80&w=1000&auto=format&fit=crop"

    if ruta.get('created_at'):
        ruta['fecha_bonita'] = ruta['created_at'].strftime("%d/%m/%Y")
    else:
        ruta['fecha_bonita'] = "Reciente"
    
    return ruta

def obtener_feed_usuario(user_id):
    rutas_crudas = home_repo.obtener_rutas_feed(user_id)
    # Usamos la función auxiliar para procesar cada ruta de la lista
    return [procesar_datos_ruta(ruta) for ruta in rutas_crudas]

def obtener_ruta_por_id(ruta_id, usuario_id):
    """
    Busca una ruta específica y la procesa para que sea 
    compatible con render_publication.
    """
    # Llamamos al repo (asegúrate de tener esta función en home_repo.py)
    ruta_cruda = home_repo.obtener_ruta_especifica(ruta_id, usuario_id)
    
    if ruta_cruda:
        return procesar_datos_ruta(ruta_cruda)
    return None

def gestionar_like(user_id, route_id, estado_actual):
    home_repo.alternar_like(user_id, route_id, estado_actual)

def gestionar_favorito(user_id, route_id, estado_actual):
    home_repo.alternar_favorito(user_id, route_id, estado_actual)

def obtener_nombres_likes(route_id):
    return home_repo.obtener_usuarios_like(route_id)

def obtener_comentarios_ruta(route_id):
    return home_repo.obtener_comentarios(route_id)

def publicar_comentario(user_id, route_id, content):
    return home_repo.insertar_comentario(user_id, route_id, content)

def obtener_estado_interacciones(route_id, user_id):
    return home_repo.obtener_estado_interacciones(route_id, user_id)