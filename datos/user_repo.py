# datos/user_repo.py
import psycopg2
from psycopg2.errors import UniqueViolation
# ¡NUEVA IMPORTACIÓN!
from datos.db_connection import get_connection, release_connection

def conseguir_usuario(username):
    # Busca un usuario en la BD por su nombre de usuario."
    conexion = get_connection() # Pedimos la conexión de la piscina
    
    if not conexion:
        return None
        
    try:
        # Consulta SQL (Asegúrate de que tu tabla se llama 'users' o cámbialo aquí)
        with conexion.cursor() as cursor:
            query = "SELECT id, username, password_hash FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            return cursor.fetchone()  
            
    except Exception as e:
        print(f"❌ Error en la consulta SQL: {e}")
        return None
    finally:
        # ¡Devolvemos la conexión a la piscina en lugar de cerrarla!
        release_connection(conexion)

def crear_usuario(username, email, password_hash):
    """Inserta un nuevo usuario en la base de datos."""
    conexion = get_connection()
    if not conexion:
        return False
        
    try:
        with conexion.cursor() as cursor:
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
        release_connection(conexion)

def get_user_data(user_id):
    """Obtiene info de la tabla 'users'."""
    conexion = get_connection()
    if not conexion:
        return None
    try:
        with conexion.cursor() as cursor:
            query = "SELECT username, bio, avatar_url, email FROM users WHERE id = %s"
            cursor.execute(query, (user_id,))
            return cursor.fetchone()
    finally:
        release_connection(conexion)

def get_social_counts(user_id):
    """Obtiene conteos de la tabla 'follows'."""
    conexion = get_connection()
    if not conexion:
        return 0, 0
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM follows WHERE followed_id = %s", (user_id,))
            seguidores = cursor.fetchone()[0] # type: ignore
            cursor.execute("SELECT COUNT(*) FROM follows WHERE follower_id = %s", (user_id,))
            seguidos = cursor.fetchone()[0] # type: ignore
            return seguidores, seguidos
    finally:
        release_connection(conexion)

def get_user_routes(user_id):
    conexion = get_connection()
    if not conexion: return []
    
    try:
        with conexion.cursor() as cursor:
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
            
    except Exception as e:
        print(f"Error al obtener las rutas: {e}")
        return []
    finally:
        release_connection(conexion)

def obtener_estado_interacciones(route_id, user_id):
    """Devuelve si el usuario logueado tiene like y fav en esta ruta."""
    conexion = get_connection()
    if not conexion: return False, False
    
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT 1 FROM likes WHERE user_id = %s AND route_id = %s", (user_id, route_id))
            has_liked = cursor.fetchone() is not None
            cursor.execute("SELECT 1 FROM favorites WHERE user_id = %s AND route_id = %s", (user_id, route_id))
            has_fav = cursor.fetchone() is not None
            return has_liked, has_fav
    finally:
        release_connection(conexion)

def delete_route_db(route_id, user_id):
    """Elimina la ruta de la DB."""
    conexion = get_connection()
    if not conexion: return False
    
    try:
        with conexion.cursor() as cursor:
            query = "DELETE FROM routes WHERE id = %s AND creator_id = %s"
            cursor.execute(query, (route_id, user_id))
            conexion.commit()
            return True
    except Exception as e:
        print(f"Error al borrar ruta en DB: {e}")
        conexion.rollback()
        return False
    finally:
        release_connection(conexion)

def obtener_interacciones_en_vivo(route_id, user_id):
    """Devuelve si el usuario le dio like, fav y el total de likes en tiempo real."""
    conexion = get_connection()
    if not conexion: return False, False, 0
    
    try:
        with conexion.cursor() as cursor:
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
        release_connection(conexion)

def update_user_full(user_id, username, email, bio, password_plana, avatar_url):
    conexion = get_connection()
    if not conexion: return False
    
    try:
        with conexion.cursor() as cursor:
            # Campos básicos
            query = "UPDATE users SET username = %s, email = %s, bio = %s"
            params = [username, email, bio]
            
            # Si el usuario escribió algo en el campo password
            if password_plana:
                query += ", password_hash = %s" 
                params.append(password_plana)
                
            if avatar_url:
                query += ", avatar_url = %s"
                params.append(avatar_url)
                
            query += " WHERE id = %s"
            params.append(user_id)
            
            cursor.execute(query, tuple(params))
            conexion.commit()
            return True
            
    except Exception as e:
        print(f"Error update_user_full: {e}")
        conexion.rollback()
        return False
    finally:
        release_connection(conexion)