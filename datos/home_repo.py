from datos.db_connection import connect

def obtener_rutas_feed(user_id):
    cursor = connect()
    if not cursor: return []
    try:
        query = """
            SELECT 
                r.id, 
                r.creator_id,  -- <--- ESTA ES LA LÍNEA QUE FALTA
                r.name, 
                r.description, 
                r.thumbnail_url, 
                r.created_at,
                r.tags, 
                u.username,
                (SELECT COUNT(*) FROM likes WHERE route_id = r.id) as num_likes,
                EXISTS(SELECT 1 FROM likes WHERE route_id = r.id AND user_id = %s) as user_has_liked,
                EXISTS(SELECT 1 FROM favorites WHERE route_id = r.id AND user_id = %s) as user_has_favorited
            FROM routes r
            JOIN follows f ON r.creator_id = f.followed_id
            JOIN users u ON r.creator_id = u.id
            WHERE f.follower_id = %s
            ORDER BY r.created_at DESC;
        """
        cursor.execute(query, (user_id, user_id, user_id))
        
        columnas = [desc[0] for desc in cursor.description] # type: ignore
        filas = cursor.fetchall()
        return [dict(zip(columnas, fila)) for fila in filas]
    # ... resto del código igual
        
    except Exception as e:
        print(f"❌ Error en feed: {e}")
        return []
    finally:
        if cursor and cursor.connection: 
            cursor.connection.close()

def alternar_like(user_id, route_id, estado_actual):
    cursor = connect()
    if not cursor: return
    try:
        if estado_actual:
            cursor.execute("DELETE FROM likes WHERE user_id = %s AND route_id = %s", (user_id, route_id))
        else:
            cursor.execute("INSERT INTO likes (user_id, route_id) VALUES (%s, %s)", (user_id, route_id))
        
        cursor.connection.commit()
    finally:
        if cursor and cursor.connection: 
            cursor.connection.close()

def alternar_favorito(user_id, route_id, estado_actual):
    """Inserta o elimina de la tabla favorites"""
    cursor = connect()
    if not cursor: return
    try:
        if estado_actual:
            # Si ya es favorito, lo quitamos
            cursor.execute("DELETE FROM favorites WHERE user_id = %s AND route_id = %s", (user_id, route_id))
        else:
            # Si no lo es, lo añadimos
            cursor.execute("INSERT INTO favorites (user_id, route_id) VALUES (%s, %s)", (user_id, route_id))
        
        cursor.connection.commit()
    except Exception as e:
        print(f"❌ Error en favorito: {e}")
    finally:
        if cursor and cursor.connection: 
            cursor.connection.close()

def obtener_usuarios_like(route_id):
    cursor = connect()
    if not cursor: return []
    try:
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
    finally:
        if cursor and cursor.connection: 
            cursor.connection.close()

def obtener_comentarios(route_id):
    cursor = connect()
    if not cursor: return []
    try:
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
    finally:
        if cursor and cursor.connection: 
            cursor.connection.close()

def insertar_comentario(user_id, route_id, content):
    cursor = connect()
    if not cursor: return
    try:
        query = "INSERT INTO comments (user_id, route_id, content) VALUES (%s, %s, %s)"
        cursor.execute(query, (user_id, route_id, content))
        cursor.connection.commit()
    finally:
        if cursor and cursor.connection: 
            cursor.connection.close()