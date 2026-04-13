from datos.db_connection import connect, close

def obtener_rutas_feed(user_id):
    cursor = connect()
    if not cursor: return []
    conexion = cursor.connection
    rutas = []
    try:
        # La consulta sigue siendo perfecta para tu esquema
        query = """
            SELECT r.id, r.name, r.description, r.thumbnail_url, r.created_at,
                   u.username, u.avatar_url,
                   (SELECT COUNT(*) FROM likes WHERE route_id = r.id) as num_likes,
                   EXISTS(SELECT 1 FROM likes WHERE route_id = r.id AND user_id = %s) as mi_like
            FROM routes r
            JOIN follows f ON r.creator_id = f.followed_id
            JOIN users u ON r.creator_id = u.id
            WHERE f.follower_id = %s
            ORDER BY r.created_at DESC;
        """
        cursor.execute(query, (user_id, user_id))
        filas = cursor.fetchall()
        for fila in filas:
            rutas.append({
                "id": fila[0], "name": fila[1], "description": fila[2],
                "thumbnail_url": fila[3], "created_at": fila[4],
                "username": fila[5], "avatar_url": fila[6],
                "num_likes": fila[7], "mi_like": fila[8]
            })
        return rutas
    except Exception as e:
        print(f"❌ Error en feed PostGIS: {e}")
        return []
    finally:
        cursor.close()
        close(conexion)

def alternar_like(user_id, route_id, dar_like):
    cursor = connect()
    if not cursor: return
    conexion = cursor.connection
    try:
        if dar_like:
            cursor.execute("INSERT INTO likes (user_id, route_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (user_id, route_id))
        else:
            cursor.execute("DELETE FROM likes WHERE user_id = %s AND route_id = %s", (user_id, route_id))
        conexion.commit()
    except Exception:
        conexion.rollback()
    finally:
        cursor.close()
        close(conexion)

def obtener_usuarios_like(route_id):
    cursor = connect()
    if not cursor: return []
    conexion = cursor.connection
    try:
        query = "SELECT u.username FROM likes l JOIN users u ON l.user_id = u.id WHERE l.route_id = %s"
        cursor.execute(query, (route_id,))
        return [fila[0] for fila in cursor.fetchall()]
    except Exception: return []
    finally:
        cursor.close()
        close(conexion)

# 🚀 NUEVO: Gestión de Comentarios
def obtener_comentarios(route_id):
    cursor = connect()
    if not cursor: return []
    conexion = cursor.connection
    try:
        query = """
            SELECT c.content, u.username, c.created_at 
            FROM comments c 
            JOIN users u ON c.user_id = u.id 
            WHERE c.route_id = %s 
            ORDER BY c.created_at ASC
        """
        cursor.execute(query, (route_id,))
        return [{"content": f[0], "username": f[1], "created_at": f[2]} for f in cursor.fetchall()]
    except Exception: return []
    finally:
        cursor.close()
        close(conexion)

def insertar_comentario(user_id, route_id, content):
    cursor = connect()
    if not cursor: return False
    conexion = cursor.connection
    try:
        cursor.execute("INSERT INTO comments (user_id, route_id, content) VALUES (%s, %s, %s)", (user_id, route_id, content))
        conexion.commit()
        return True
    except Exception:
        conexion.rollback()
        return False
    finally:
        cursor.close()
        close(conexion)