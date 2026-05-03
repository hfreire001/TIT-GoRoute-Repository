# datos/search_repo.py
from datos.db_connection import get_connection, release_connection

def search_routes_by_tags(seleccionados):
    conexion = get_connection()
    if not conexion: 
        return []
        
    try:
        with conexion.cursor() as cursor:
            # Usamos el operador de solapamiento de arrays && de PostgreSQL
            query = """
                SELECT 
                    r.id, r.name, r.creator_id, r.tags, r.thumbnail_url,
                    u.username,
                    (SELECT COUNT(*) FROM likes WHERE route_id = r.id) as likes,
                    (SELECT COUNT(*) FROM comments WHERE route_id = r.id) as comentarios,
                    (SELECT COUNT(*) FROM favorites WHERE route_id = r.id) as guardados
                FROM routes r
                JOIN users u ON r.creator_id = u.id
                WHERE r.tags && %s
            """
            cursor.execute(query, (seleccionados,))
            
            # Convertimos los resultados a un diccionario asociando el nombre de la columna
            if cursor.description is not None:
                columnas = [desc[0] for desc in cursor.description]
                return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
            return []
            
    except Exception as e:
        print(f"❌ Error en search_routes_by_tags: {e}")
        return []
    finally:
        # Devolvemos la conexión a la piscina
        release_connection(conexion)

def get_top_liked_routes():
    conexion = get_connection()
    if not conexion: 
        return []
        
    try:
        with conexion.cursor() as cursor:
            # Usamos la misma estructura de subconsultas que en la búsqueda por tags
            # para traer toda la info necesaria para el hover del frontend.
            sql = """
                SELECT 
                    r.id, r.name, r.creator_id, u.username,
                    (SELECT COUNT(*) FROM likes WHERE route_id = r.id) as likes,
                    (SELECT COUNT(*) FROM comments WHERE route_id = r.id) as comentarios,
                    (SELECT COUNT(*) FROM favorites WHERE route_id = r.id) as guardados
                FROM routes r
                JOIN users u ON r.creator_id = u.id
                ORDER BY likes DESC LIMIT 6
            """
            cursor.execute(sql)
            
            # Lo devolvemos como diccionario en lugar de tupla, ¡mucho más seguro!
            if cursor.description is not None:
                columnas = [desc[0] for desc in cursor.description]
                return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
            return []
            
    except Exception as e:
        print(f"❌ Error en get_top_liked_routes: {e}")
        return []
    finally:
        release_connection(conexion)