from datos.db_connection import connect, close

def search_routes_by_tags(tag_list):
    cursor = connect()
    if not cursor: return []
    try:
        # El operador && busca rutas donde el array de la BBDD tenga 
        # cualquier elemento en común con el array que le pasamos.
        sql = "SELECT id, name, creator_id, tags FROM routes WHERE tags && %s"
        
        # Pasamos la lista de Python directamente, el driver la convierte a array de Postgres
        cursor.execute(sql, (tag_list,))
        return cursor.fetchall()
    finally:
        close(cursor.connection)

def get_top_liked_routes():
    cursor = connect()
    if not cursor: return []
    try:
        # Usamos COUNT(l.route_id) o COUNT(*) para evitar el error de la columna l.id
        sql = """
            SELECT r.id, r.name, r.creator_id, COUNT(l.route_id) as likes
            FROM routes r
            LEFT JOIN likes l ON r.id = l.route_id
            GROUP BY r.id, r.name, r.creator_id
            ORDER BY likes DESC LIMIT 6
        """
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        close(cursor.connection)