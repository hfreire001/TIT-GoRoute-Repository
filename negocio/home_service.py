import os
from datos import home_repo

# Ruta base dinámica (más segura que hardcodear C:\...)
BASE_PATH = r"C:\Users\garaz\OneDrive\Escritorio\UNIVERSIDAD\Cuarto\TAP\Plan&Go"

def obtener_feed_usuario(user_id):
    rutas_crudas = home_repo.obtener_rutas_feed(user_id)
    rutas_procesadas = []
    
    for ruta in rutas_crudas:
        path_bbdd = ruta.get('thumbnail_url') 
        
        # Procesamiento de imagen
        if path_bbdd:
            path_limpio = os.path.normpath(path_bbdd.lstrip("\\/"))
            path_local = os.path.join(BASE_PATH, path_limpio)
            
            if os.path.exists(path_local):
                with open(path_local, "rb") as f:
                    ruta['imagen_bytes'] = f.read()
            else:
                ruta['imagen_bytes'] = "https://images.unsplash.com/photo-1551632811-561732d1e306?q=80&w=1000&auto=format&fit=crop"
        else:
            ruta['imagen_bytes'] = "https://images.unsplash.com/photo-1551632811-561732d1e306?q=80&w=1000&auto=format&fit=crop"

        # Formateo de fecha
        if ruta.get('created_at'):
            ruta['fecha_bonita'] = ruta['created_at'].strftime("%d/%m/%Y")
        else:
            ruta['fecha_bonita'] = "Reciente"
            
        rutas_procesadas.append(ruta)
        
    return rutas_procesadas

def gestionar_like(user_id, route_id, estado_actual):
    home_repo.alternar_like(user_id, route_id, estado_actual)

def gestionar_favorito(user_id, route_id, estado_actual):
    """Llamada al repositorio para guardar/quitar de favoritos"""
    home_repo.alternar_favorito(user_id, route_id, estado_actual)

def obtener_nombres_likes(route_id):
    return home_repo.obtener_usuarios_like(route_id)

def obtener_comentarios_ruta(route_id):
    return home_repo.obtener_comentarios(route_id)

def publicar_comentario(user_id, route_id, content):
    return home_repo.insertar_comentario(user_id, route_id, content)