import os
import glob
from datos import user_repo

def delete_route(route_id, user_id):
    """
    Borra la ruta de la base de datos y su imagen física.
    Al usar el ID como nombre, ya no necesitamos reordenar archivos.
    """
    # 1. Borramos de la base de datos
    db_success = user_repo.delete_route_db(route_id, user_id)
    
    if db_success:
        # 2. Borramos el archivo físico (buscamos cualquier extensión con ese ID)
        # Ruta: imagenes/{user_id}/rutas/{route_id}.*
        patron_borrar = rf"C:\Users\garaz\OneDrive\Escritorio\UNIVERSIDAD\Cuarto\TAP\Plan&Go\imagenes\{user_id}\rutas\{route_id}.*"
        
        for f in glob.glob(patron_borrar):
            try:
                os.remove(f)
            except Exception as e:
                print(f"Error al eliminar archivo físico: {e}")
                
    return db_success

def get_full_profile(user_id):
    user_raw = user_repo.get_user_data(user_id)
    if not user_raw: return None

    seguidores, seguidos = user_repo.get_social_counts(user_id)
    routes_raw = user_repo.get_user_routes(user_id) 

    # 1. Avatar
    foto_perfil = "https://www.w3schools.com/howto/img_avatar.png"
    base_avatar = rf"C:\Users\garaz\OneDrive\Escritorio\UNIVERSIDAD\Cuarto\TAP\Plan&Go\imagenes\{user_id}\avatar\imagen1"
    
    for ext in ['jpg', 'png', 'jpeg', 'webp']:
        if os.path.exists(f"{base_avatar}.{ext}"):
            # Para mostrar en Streamlit, usamos la ruta relativa
            foto_perfil = f"imagenes/{user_id}/avatar/imagen1.{ext}"
            break

    # 2. Rutas (Buscando por ID de ruta)
    rutas_procesadas = []
    
    for r in routes_raw:
        r_id = r[0]         # El ID real (ej: 15)
        r_name = r[1]
        r_likes = r[2]
        r_comments = r[3]
        r_saved = r[4]

        # Por defecto, imagen de relleno
        ruta_img = "https://via.placeholder.com/300x200?text=Sin+Imagen"
        
        # Buscamos el archivo que se llame exactamente como el ID (ej: 15.jpg)
        base_ruta_fisica = rf"C:\Users\garaz\OneDrive\Escritorio\UNIVERSIDAD\Cuarto\TAP\Plan&Go\imagenes\{user_id}\rutas\{r_id}"
        
        for ext in ['jpg', 'png', 'jpeg', 'webp']:
            if os.path.exists(f"{base_ruta_fisica}.{ext}"):
                # Si existe, devolvemos la ruta relativa para que Streamlit la cargue
                ruta_img = f"imagenes/{user_id}/rutas/{r_id}.{ext}"
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