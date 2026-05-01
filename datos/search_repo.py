from datos.db_connection import connect, close

def search_routes_by_tags(seleccionados):
    cursor = connect()
    if not cursor: return []
    try:
        # Usamos ANY para buscar en el array de PostgreSQL
        query = """
            SELECT 
                r.id, r.name, r.creator_id, r.tags, r.thumbnail_url,
                u.username,
                (SELECT COUNT(*) FROM likes WHERE route_id = r.id) as likes,
                (SELECT COUNT(*) FROM comments WHERE route_id = r.id) as comentarios,
                (SELECT COUNT(*) FROM favorites WHERE route_id = r.id) as guardados
            FROM routes r
            JOIN users u ON r.creator_id = u.id
            WHERE r.tags && %s  -- Operador de solapamiento de arrays
        """
        cursor.execute(query, (seleccionados,))
        
        if cursor.description is not None:
            columnas = [desc[0] for desc in cursor.description]
            return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        return []
    finally:
        close(cursor.connection)

def get_top_liked_routes():
    cursor = connect()
    if not cursor: return []
    try:
        # Añadimos u.username para las tendencias
        sql = """
            SELECT r.id, r.name, r.creator_id, COUNT(l.route_id) as likes, u.username
            FROM routes r
            LEFT JOIN likes l ON r.id = l.route_id
            JOIN users u ON r.creator_id = u.id
            GROUP BY r.id, r.name, r.creator_id, u.username
            ORDER BY likes DESC LIMIT 6
        """
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        close(cursor.connection)