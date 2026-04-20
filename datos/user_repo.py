from datos.db_connection import connect, close
from psycopg2.errors import UniqueViolation
#Crear la clase de usuario
#Métodos que generan query 

def conseguir_usuario(username):
    # Busca un usuario en la BD por su nombre de usuario."
    cursor = connect()
    
    if not cursor:
        return None
        
    # Extraemos la conexión del propio cursor para poder cerrarla luego
    conexion = cursor.connection
        
    try:
        # Consulta SQL (Asegúrate de que tu tabla se llama 'users' o cámbialo aquí)
        query = "SELECT id, username, password_hash FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        return cursor.fetchone()  
            
    except Exception as e:
        print(f"❌ Error en la consulta SQL: {e}")
        return None
    finally:
        # Cerramos el cursor y usamos TU función close() pasándole la conexión
        cursor.close()
        close(conexion)

def crear_usuario(username, email, password_hash):
    """Inserta un nuevo usuario en la base de datos."""
    cursor = connect()
    if not cursor:
        return False
        
    conexion = cursor.connection
    try:
        query = "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, email, password_hash))
        conexion.commit() # ¡Guardamos los cambios en la BD!
        return True
        
    except UniqueViolation:
        # Si el usuario o correo ya existe (porque la BD tiene restricciones UNIQUE)
        conexion.rollback()
        return False
    except Exception as e:
        print(f"❌ Error insertando usuario: {e}")
        conexion.rollback()
        return False
    finally:
        cursor.close()
        close(conexion)
# datos/user_repo.py
from datos.db_connection import connect, close

def get_user_data(user_id):
    """Obtiene info de la tabla 'users'."""
    cursor = connect()
    if not cursor:
        return None
    try:
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

def get_user_routes(user_id):
    """Obtiene las rutas con sus respectivos contadores de interacción."""
    cursor = connect()
    if not cursor: return []
    try:
        # Añadimos subconsultas para contar likes, comentarios y favoritos
        query = """
            SELECT 
                r.id, 
                r.name, 
                (SELECT COUNT(*) FROM likes WHERE route_id = r.id) as total_likes,
                (SELECT COUNT(*) FROM comments WHERE route_id = r.id) as total_comments,
                (SELECT COUNT(*) FROM favorites WHERE route_id = r.id) as total_favs,
                r.created_at
            FROM routes r
            WHERE r.creator_id = %s 
            ORDER BY r.created_at ASC
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchall() 
    finally:
        if cursor:
            conn = cursor.connection
            cursor.close()
            close(conn)

def delete_route_db(route_id, user_id):
    """Elimina la ruta de la DB."""
    cursor = connect()
    if not cursor: return False
    try:
        query = "DELETE FROM routes WHERE id = %s AND creator_id = %s"
        cursor.execute(query, (route_id, user_id))
        cursor.connection.commit()
        return True
    except Exception as e:
        print(f"Error al borrar ruta en DB: {e}")
        return False
    finally:
        if cursor:
            conn = cursor.connection
            cursor.close()
            close(conn)
