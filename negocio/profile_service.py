import os
from datos import user_repo


def delete_route(route_id, user_id):
    # Aquí podrías añadir lógica para borrar el archivo físico si quisieras
    return user_repo.delete_route_db(route_id, user_id)

# (El resto de la función get_full_profile se mantiene igual)


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