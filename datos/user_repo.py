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

def get_user_data(user_id):
    """Obtiene info de la tabla 'users'."""
    cursor = connect()
    if not cursor:
        return None
    try:
        query = "SELECT username, bio, avatar_url, email FROM users WHERE id = %s"
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
    cursor = connect()
    if not cursor: return []
    conexion = cursor.connection
    try:
        query = """
            SELECT 
                r.id, 
                r.name as nombre, 
                r.description, 
                r.tags,
                r.thumbnail_url as miniatura,
                (SELECT COUNT(*) FROM likes WHERE route_id = r.id) as likes,
                (SELECT COUNT(*) FROM comments WHERE route_id = r.id) as comentarios,
                (SELECT COUNT(*) FROM favorites WHERE route_id = r.id) as guardados
            FROM routes r
            WHERE r.creator_id = %s 
            ORDER BY r.created_at DESC
        """
        cursor.execute(query, (user_id,))
        
        # --- SOLUCIÓN AQUÍ ---
        # Verificamos que description no sea None antes de iterar
        if cursor.description is not None:
            columnas = [desc[0] for desc in cursor.description]
            return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        else:
            return []
        # ---------------------
        
    finally:
        cursor.close()
        close(conexion)

def obtener_estado_interacciones(route_id, user_id):
    """Devuelve si el usuario logueado tiene like y fav en esta ruta."""
    cursor = connect()
    if not cursor: return False, False
    conexion = cursor.connection
    try:
        cursor.execute("SELECT 1 FROM likes WHERE user_id = %s AND route_id = %s", (user_id, route_id))
        has_liked = cursor.fetchone() is not None
        cursor.execute("SELECT 1 FROM favorites WHERE user_id = %s AND route_id = %s", (user_id, route_id))
        has_fav = cursor.fetchone() is not None
        return has_liked, has_fav
    finally:
        cursor.close()
        close(conexion)

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

def obtener_interacciones_en_vivo(route_id, user_id):
    """Devuelve si el usuario le dio like, fav y el total de likes en tiempo real."""
    cursor = connect()
    if not cursor: return False, False, 0
    try:
        cursor.execute("SELECT 1 FROM likes WHERE user_id = %s AND route_id = %s", (user_id, route_id))
        has_liked = cursor.fetchone() is not None
        
        cursor.execute("SELECT 1 FROM favorites WHERE user_id = %s AND route_id = %s", (user_id, route_id))
        has_fav = cursor.fetchone() is not None
        
        cursor.execute("SELECT COUNT(*) FROM likes WHERE route_id = %s", (route_id,))
        total_likes = cursor.fetchone()[0] # type: ignore
        
        return has_liked, has_fav, total_likes
    except Exception as e:
        print(f"❌ Error al obtener interacciones: {e}")
        return False, False, 0
    finally:
        if cursor:
            conn = cursor.connection
            cursor.close()
            close(conn)

def update_user_full(user_id, username, email, bio, password_plana, avatar_url):
    cursor = connect()
    if not cursor: return False
    conn = cursor.connection
    try:
        # Campos básicos
        query = "UPDATE users SET username = %s, email = %s, bio = %s"
        params = [username, email, bio]
        
        # Si el usuario escribió algo en el campo password
        if password_plana:
            query += ", password_hash = %s" # <--- Cambia 'password_hash' por el nombre real de tu columna
            params.append(password_plana)
            
        if avatar_url:
            query += ", avatar_url = %s"
            params.append(avatar_url)
            
        query += " WHERE id = %s"
        params.append(user_id)
        
        cursor.execute(query, tuple(params))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error update_user_full: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        close(conn)