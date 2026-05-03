# datos/home_repo.py
import psycopg2.extras
from datos.db_connection import get_connection, release_connection

def obtener_rutas_feed(user_id):
    conexion = get_connection()
    if not conexion: 
        return []
        
    try:
        with conexion.cursor() as cursor:
            # Añadimos r.etiquetas a la consulta
            query = """
                SELECT 
                    r.id, 
                    r.creator_id,
                    r.name, 
                    r.description, 
                    r.thumbnail_url, 
                    r.created_at,
                    r.tags, 
                    u.username,
                    (SELECT COUNT(*) FROM likes WHERE route_id = r.id) as num_likes,
                    EXISTS(SELECT 1 FROM likes WHERE route_id = r.id AND user_id = %s) as user_has_liked
                FROM routes r
                JOIN follows f ON r.creator_id = f.followed_id
                JOIN users u ON r.creator_id = u.id
                WHERE f.follower_id = %s
                ORDER BY r.created_at DESC;
            """
            cursor.execute(query, (user_id, user_id))
            
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()
            return [dict(zip(columnas, fila)) for fila in filas]
            
    except Exception as e:
        print(f"❌ Error en feed: {e}")
        return []
    finally:
        release_connection(conexion)

def alternar_like(user_id, route_id, estado_actual):
    conexion = get_connection()
    if not conexion: 
        return
        
    try:
        with conexion.cursor() as cursor:
            if estado_actual:
                cursor.execute("DELETE FROM likes WHERE user_id = %s AND route_id = %s", (user_id, route_id))
            else:
                cursor.execute("INSERT INTO likes (user_id, route_id) VALUES (%s, %s)", (user_id, route_id))
            
            conexion.commit() # Guardamos los cambios
    except Exception as e:
        print(f"❌ Error al alternar like: {e}")
        conexion.rollback() # Revertimos en caso de error
    finally:
        release_connection(conexion)

def alternar_favorito(user_id, route_id, estado_actual):
    """Inserta o elimina de la tabla favorites"""
    conexion = get_connection()
    if not conexion: 
        return
        
    try:
        with conexion.cursor() as cursor:
            if estado_actual:
                # Si ya es favorito, lo quitamos
                cursor.execute("DELETE FROM favorites WHERE user_id = %s AND route_id = %s", (user_id, route_id))
            else:
                # Si no lo es, lo añadimos
                cursor.execute("INSERT INTO favorites (user_id, route_id) VALUES (%s, %s)", (user_id, route_id))
            
            conexion.commit()
    except Exception as e:
        print(f"❌ Error en favorito: {e}")
        conexion.rollback()
    finally:
        release_connection(conexion)

def obtener_usuarios_like(route_id):
    conexion = get_connection()
    if not conexion: 
        return []
        
    try:
        with conexion.cursor() as cursor:
            query = """
                SELECT u.username 
                FROM likes l
                JOIN users u ON l.user_id = u.id
                WHERE l.route_id = %s
            """
            cursor.execute(query, (route_id,))
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()
            return [dict(zip(columnas, fila)) for fila in filas]
    except Exception as e:
        print(f"❌ Error al obtener usuarios_like: {e}")
        return []
    finally:
        release_connection(conexion)

def obtener_comentarios(route_id):
    conexion = get_connection()
    if not conexion: 
        return []
        
    try:
        with conexion.cursor() as cursor:
            query = """
                SELECT c.content, u.username, c.created_at
                FROM comments c
                JOIN users u ON c.user_id = u.id
                WHERE c.route_id = %s
                ORDER BY c.created_at ASC
            """
            cursor.execute(query, (route_id,))
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()
            return [dict(zip(columnas, fila)) for fila in filas]
    except Exception as e:
        print(f"❌ Error al obtener comentarios: {e}")
        return []
    finally:
        release_connection(conexion)

def insertar_comentario(user_id, route_id, content):
    conexion = get_connection()
    if not conexion: 
        return
        
    try:
        with conexion.cursor() as cursor:
            query = "INSERT INTO comments (user_id, route_id, content) VALUES (%s, %s, %s)"
            cursor.execute(query, (user_id, route_id, content))
            conexion.commit()
    except Exception as e:
        print(f"❌ Error al insertar comentario: {e}")
        conexion.rollback()
    finally:
        release_connection(conexion)

def obtener_ruta_especifica(ruta_id, user_id):
    conexion = get_connection()
    if not conexion:
        return None
        
    try:
        # Usamos el RealDictCursor asociado a nuestra conexión abierta
        with conexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as dict_cursor:
            query = """
                SELECT r.*, u.username,
                       (SELECT COUNT(*) FROM likes WHERE route_id = r.id) as num_likes,
                       EXISTS(SELECT 1 FROM likes WHERE route_id = r.id AND user_id = %s) as user_has_liked,
                       EXISTS(SELECT 1 FROM favorites WHERE route_id = r.id AND user_id = %s) as user_has_favorited
                FROM routes r
                JOIN users u ON r.creator_id = u.id
                WHERE r.id = %s
            """
            dict_cursor.execute(query, (user_id, user_id, ruta_id))
            return dict_cursor.fetchone()
    except Exception as e:
        print(f"❌ Error en obtener_ruta_especifica: {e}")
        return None
    finally:
        release_connection(conexion)
        
def obtener_estado_interacciones(route_id, user_id):
    """Consulta rápida para saber si el usuario tiene like o fav en una ruta del feed."""
    conexion = get_connection()
    if not conexion: 
        return False, False
        
    try:
        with conexion.cursor() as cursor:
            # Miramos si hay like
            cursor.execute("SELECT 1 FROM likes WHERE user_id = %s AND route_id = %s", (user_id, route_id))
            has_liked = cursor.fetchone() is not None
            
            # Miramos si hay favorito
            cursor.execute("SELECT 1 FROM favorites WHERE user_id = %s AND route_id = %s", (user_id, route_id))
            has_fav = cursor.fetchone() is not None
            
            return has_liked, has_fav
    except Exception as e:
        print(f"❌ Error al obtener interacciones rápidas: {e}")
        return False, False
    finally:
        release_connection(conexion)