import os
import glob
from datos import user_repo

def delete_route(route_id, user_id):
    """Tu lógica original de borrado y reordenado de archivos"""
    routes_raw = user_repo.get_user_routes(user_id)
    indice_borrar = -1
    for index, r in enumerate(routes_raw):
        if r[0] == route_id:
            indice_borrar = index + 1
            break
    if indice_borrar == -1: return False

    db_success = user_repo.delete_route_db(route_id, user_id)
    if db_success:
        patron_borrar = f"imagenes/{user_id}/rutas/imagen{indice_borrar}.*"
        for f in glob.glob(patron_borrar):
            os.remove(f)
        total_rutas_originales = len(routes_raw)
        for i in range(indice_borrar + 1, total_rutas_originales + 1):
            patron_siguiente = f"imagenes/{user_id}/rutas/imagen{i}.*"
            for f_antiguo in glob.glob(patron_siguiente):
                extension = os.path.splitext(f_antiguo)[1]
                nuevo_nombre = f"imagenes/{user_id}/rutas/imagen{i-1}{extension}"
                try: os.rename(f_antiguo, nuevo_nombre)
                except Exception: pass
    return db_success

def get_full_profile(user_id):
    user_raw = user_repo.get_user_data(user_id)
    if not user_raw: return None

    seguidores, seguidos = user_repo.get_social_counts(user_id)
    # Obtenemos las rutas (asegúrate de que el SQL en user_repo tenga los 5 campos)
    routes_raw = user_repo.get_user_routes(user_id) 

    # 1. Avatar (Lógica original)
    foto_perfil = "https://www.w3schools.com/howto/img_avatar.png"
    base_avatar = f"imagenes/{user_id}/avatar/imagen1"
    for ext in ['jpg', 'png', 'jpeg', 'webp']:
        if os.path.exists(f"{base_avatar}.{ext}"):
            foto_perfil = f"{base_avatar}.{ext}"
            break

    # 2. Rutas con lógica de archivos + CONTADORES
    rutas_procesadas = []
    
    # --- AQUÍ SE INTEGRA EL BLOQUE QUE PEDISTE ---
    for index, r in enumerate(routes_raw):
        r_id = r[0]
        r_name = r[1]
        r_likes = r[2]      # Conteo de likes
        r_comments = r[3]   # Conteo de comentarios
        r_saved = r[4]      # Conteo de favoritos/guardados

        # Lógica para encontrar la imagen física correspondiente
        n_imagen = index + 1
        ruta_img = "https://via.placeholder.com/300x200?text=Sin+Imagen"
        base_ruta = f"imagenes/{user_id}/rutas/imagen{n_imagen}"
        
        for ext in ['jpg', 'png', 'jpeg', 'webp']:
            if os.path.exists(f"{base_ruta}.{ext}"):
                ruta_img = f"{base_ruta}.{ext}"
                break
        
        rutas_procesadas.append({
            "id": r_id,
            "nombre": r_name,
            "miniatura": ruta_img,
            "likes": r_likes,
            "comentarios": r_comments,
            "guardados": r_saved
        })

    return {
        "username": user_raw[0],
        "bio": user_raw[1],
        "foto": foto_perfil,
        "seguidores": seguidores,
        "seguidos": seguidos,
        "rutas": rutas_procesadas
    }