# negocio/profile_service.py
from datos import user_repo

def get_full_profile(user_id):
    raw_user = user_repo.get_user_data(user_id)
    if not raw_user:
        return None

    seguidores, seguidos = user_repo.get_social_counts(user_id)
    rutas_raw = user_repo.get_user_routes(user_id)

    return {
        "username": raw_user[0],
        "bio": raw_user[1] if raw_user[1] else "Sin biografía.",
        "foto": raw_user[2] if raw_user[2] else "https://www.w3schools.com/howto/img_avatar.png",
        "seguidores": seguidores,
        "seguidos": seguidos,
        "rutas": [
            {
                "id": r[0],
                "nombre": r[1],
                "miniatura": r[2] if r[2] else "https://via.placeholder.com/300x200?text=Ruta"
            } for r in rutas_raw
        ]
    }