# datos/user_repo.py
from datos.db_connection import connect, close

def get_user_data(user_id):
    """Obtiene info de la tabla 'users'."""
    cursor = connect()
    if not cursor:
        return None
    try:
        # Ajustado a tus columnas: username, bio, avatar_url
        query = "SELECT username, bio, avatar_url FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        return cursor.fetchone()
    finally:
        if cursor:
            conn = cursor.connection
            cursor.close()
            close(conn)

def get_social_counts(user_id):
    """Obtiene conteos de la tabla 'follows'."""
    cursor = connect()
    if not cursor:
        return 0, 0
    try:
        # follower_id: el que sigue | followed_id: el que es seguido
        cursor.execute("SELECT COUNT(*) FROM follows WHERE followed_id = %s", (user_id,))
        seguidores = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM follows WHERE follower_id = %s", (user_id,))
        seguidos = cursor.fetchone()[0]
        return seguidores, seguidos
    finally:
        if cursor:
            conn = cursor.connection
            cursor.close()
            close(conn)

def get_user_routes(user_id):
    """Obtiene rutas de la tabla 'routes'."""
    cursor = connect()
    if not cursor:
        return []
    try:
        # Ajustado a tus columnas: id, name, thumbnail_url
        query = "SELECT id, name, thumbnail_url FROM routes WHERE creator_id = %s"
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    finally:
        if cursor:
            conn = cursor.connection
            cursor.close()
            close(conn)