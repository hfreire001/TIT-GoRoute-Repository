import os
import glob
from datos import user_repo

# Base path para imágenes
BASE_PATH = r"C:\Users\garaz\OneDrive\Escritorio\UNIVERSIDAD\Cuarto\TAP\Plan&Go"

def delete_route(route_id, user_id):
    """Borra la ruta de la base de datos y su imagen física."""
    db_success = user_repo.delete_route_db(route_id, user_id)
    if db_success:
        patron_borrar = os.path.join(BASE_PATH, "imagenes", str(user_id), "rutas", f"{route_id}.*")
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
    # Buscamos en la carpeta local
    ruta_avatar_folder = os.path.join(BASE_PATH, "imagenes", str(user_id), "avatar")
    
    if os.path.exists(ruta_avatar_folder):
        for f in os.listdir(ruta_avatar_folder):
            if f.startswith("imagen1"):
                foto_perfil = os.path.join("imagenes", str(user_id), "avatar", f)
                break

    # 2. Rutas
    rutas_procesadas = []
    for r in routes_raw:
        r_id, r_name, r_likes, r_comments, r_saved = r[0], r[1], r[2], r[3], r[4]
        
        ruta_img = "https://via.placeholder.com/300x200?text=Sin+Imagen"
        ruta_fisica_folder = os.path.join(BASE_PATH, "imagenes", str(user_id), "rutas")
        
        if os.path.exists(ruta_fisica_folder):
            for ext in ['jpg', 'png', 'jpeg', 'webp']:
                if os.path.exists(os.path.join(ruta_fisica_folder, f"{r_id}.{ext}")):
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