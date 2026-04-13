import os
import glob
from datos import user_repo


# negocio/profile_service.py
import os
import glob
from datos import user_repo

def delete_route(route_id, user_id):
    """Elimina una ruta y reordena los archivos físicos para no dejar huecos."""
    
    # 1. Obtener la lista de rutas ANTES de borrar para saber la posición
    routes_raw = user_repo.get_user_routes(user_id)
    
    indice_borrar = -1
    for index, r in enumerate(routes_raw):
        if r[0] == route_id:
            indice_borrar = index + 1 # Posición natural (1, 2, 3...)
            break

    if indice_borrar == -1:
        return False

    # 2. Borrar de la Base de Datos
    db_success = user_repo.delete_route_db(route_id, user_id)
    
    if db_success:
        # 3. Borrar el archivo físico correspondiente
        # Buscamos imagenN.* (cualquier extensión)
        patron_borrar = f"imagenes/{user_id}/rutas/imagen{indice_borrar}.*"
        for f in glob.glob(patron_borrar):
            os.remove(f)

        # 4. RENOMBRAR LOS POSTERIORES (Shift hacia atrás)
        # Ejemplo: Si borramos imagen1, la imagen2 pasa a ser imagen1, la 3 a 2...
        total_rutas_originales = len(routes_raw)
        
        for i in range(indice_borrar + 1, total_rutas_originales + 1):
            # Buscamos el archivo de la siguiente posición (i)
            patron_siguiente = f"imagenes/{user_id}/rutas/imagen{i}.*"
            for f_antiguo in glob.glob(patron_siguiente):
                # Extraemos la extensión original (.jpg, .png...)
                extension = os.path.splitext(f_antiguo)[1]
                # Nuevo nombre: una posición menos
                nuevo_nombre = f"imagenes/{user_id}/rutas/imagen{i-1}{extension}"
                
                try:
                    os.rename(f_antiguo, nuevo_nombre)
                    print(f"Renombrado: {f_antiguo} -> {nuevo_nombre}")
                except Exception as e:
                    print(f"Error renombrando {f_antiguo}: {e}")

    return db_success


def get_full_profile(user_id):
    user_raw = user_repo.get_user_data(user_id)
    if not user_raw: return None

    seguidores, seguidos = user_repo.get_social_counts(user_id)
    routes_raw = user_repo.get_user_routes(user_id)

    # 1. Avatar: Siempre imagen1 (buscamos cualquier extensión común)
    foto_perfil = "https://www.w3schools.com/howto/img_avatar.png" # Default
    base_avatar = f"imagenes/{user_id}/avatar/imagen1"
    
    for ext in ['jpg', 'png', 'jpeg', 'webp']:
        if os.path.exists(f"{base_avatar}.{ext}"):
            foto_perfil = f"{base_avatar}.{ext}"
            break

    # 2. Rutas: imagen1, imagen2... según el orden en la lista
    rutas_procesadas = []
    for index, r in enumerate(routes_raw):
        r_id, r_name, _ = r
        n_imagen = index + 1 # El primer elemento es imagen1
        
        # Buscamos el archivo imagenX.ext
        ruta_img = "https://via.placeholder.com/300x200?text=Sin+Imagen"
        base_ruta = f"imagenes/{user_id}/rutas/imagen{n_imagen}"
        
        for ext in ['jpg', 'png', 'jpeg', 'webp']:
            if os.path.exists(f"{base_ruta}.{ext}"):
                ruta_img = f"{base_ruta}.{ext}"
                break
        
        rutas_procesadas.append({
            "id": r_id,
            "nombre": r_name,
            "miniatura": ruta_img
        })

    return {
        "username": user_raw[0],
        "bio": user_raw[1],
        "foto": foto_perfil,
        "seguidores": seguidores,
        "seguidos": seguidos,
        "rutas": rutas_procesadas
    }