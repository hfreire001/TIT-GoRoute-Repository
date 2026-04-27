from datos.db_connection import connect, close

def search_routes_by_tags(tag_list):
    cursor = connect()
    if not cursor: return []
    try:
        # Añadimos u.username y el JOIN con la tabla users
        sql = """
            SELECT r.id, r.name, r.creator_id, r.tags, u.username 
            FROM routes r
            JOIN users u ON r.creator_id = u.id
            WHERE r.tags && %s
        """
        cursor.execute(sql, (tag_list,))
        return cursor.fetchall()
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