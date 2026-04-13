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
        seguidores = cursor.fetchone()[0] # type: ignore
        cursor.execute("SELECT COUNT(*) FROM follows WHERE follower_id = %s", (user_id,))
        seguidos = cursor.fetchone()[0] # type: ignore
        return seguidores, seguidos
    finally:
        if cursor:
            conn = cursor.connection
            cursor.close()
            close(conn)

# datos/user_repo.py
from datos.db_connection import connect, close

def get_user_routes(user_id):
    cursor = connect()
    if not cursor: return []
    try:
        # Ordenamos por fecha de creación para que la primera sea imagen1, la segunda imagen2...
        query = """
            SELECT id, name, created_at 
            FROM routes 
            WHERE creator_id = %s 
            ORDER BY created_at ASC
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchall() 
    finally:
        if cursor:
            conn = cursor.connection
            cursor.close()
            close(conn)
            
# datos/user_repo.py

def delete_route_db(route_id, user_id):
    """Elimina la ruta de la DB verificando que el creador sea el usuario logueado."""
    cursor = connect()
    if not cursor: return False
    try:
        query = "DELETE FROM routes WHERE id = %s AND creator_id = %s"
        cursor.execute(query, (route_id, user_id))
        cursor.connection.commit() # Confirmamos el borrado
        return True
    except Exception as e:
        print(f"Error al borrar ruta en DB: {e}")
        return False
    finally:
        if cursor:
            conn = cursor.connection
            cursor.close()
            close(conn)