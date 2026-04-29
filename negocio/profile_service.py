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
    user_data = user_repo.get_user_data(user_id)
    if not user_data: return None

    username, bio, avatar_url, email = user_data
    seguidores, seguidos = user_repo.get_social_counts(user_id)
    # Vienen como diccionarios directos del repo
    rutas_procesadas = user_repo.get_user_routes(user_id)

    return {
        "username": username,
        "bio": bio if bio else "",
        "foto": avatar_url,
        "email": email if email else "", # 🚀 ESTA LÍNEA ES CLAVE
        "seguidores": seguidores,
        "seguidos": seguidos,
        "rutas": rutas_procesadas
    }

def obtener_estado_interacciones(route_id, user_id):
    return user_repo.obtener_estado_interacciones(route_id, user_id)

import os
import bcrypt
from datos import user_repo

import os
from datos import user_repo

def actualizar_perfil_completo(user_id, username, email, bio, password, imagen_file):
    # 1. Procesar contraseña: si tiene texto, la pasamos tal cual
    pw_final = None
    if password and password.strip():
        pw_final = password.strip()
    
    # 2. Procesar imagen si se subió una nueva
    avatar_url = None
    if imagen_file:
        ext = imagen_file.name.split('.')[-1]
        filename = f"avatar_{user_id}.{ext}"
        folder = os.path.join("imagenes", str(user_id), "perfil")
        os.makedirs(folder, exist_ok=True)
        path_fisico = os.path.join(folder, filename)
        
        with open(path_fisico, "wb") as f:
            f.write(imagen_file.getbuffer())
        
        avatar_url = f"imagenes/{user_id}/perfil/{filename}"
    
    # 3. Llamar al repositorio con la pass en texto plano
    return user_repo.update_user_full(user_id, username, email, bio, pw_final, avatar_url)