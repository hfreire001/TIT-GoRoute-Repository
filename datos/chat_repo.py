# datos/chat_repo.py
from datos.db_connection import get_connection, release_connection

def obtener_lista_chats(user_id):
    conexion = get_connection()
    if not conexion:
        return []
    try:
        with conexion.cursor() as cursor:
            query = """
            SELECT u.id, u.username, u.avatar_url, m.content, m.created_at
            FROM users u
            JOIN (
                SELECT 
                    CASE WHEN sender_id = %s THEN receiver_id ELSE sender_id END as other_user_id,
                    content, created_at,
                    ROW_NUMBER() OVER(PARTITION BY CASE WHEN sender_id = %s THEN receiver_id ELSE sender_id END ORDER BY created_at DESC) as rn
                FROM messages
                WHERE sender_id = %s OR receiver_id = %s
            ) m ON u.id = m.other_user_id
            WHERE m.rn = 1
            ORDER BY m.created_at DESC;
            """
            cursor.execute(query, (user_id, user_id, user_id, user_id))
            return cursor.fetchall()
    except Exception as e:
        print(f"❌ Error en obtener_lista_chats: {e}")
        return []
    finally:
        release_connection(conexion)

def buscar_usuarios_para_chat(user_id, search_text):
    conexion = get_connection()
    if not conexion:
        return []
    try:
        with conexion.cursor() as cursor:
            query = """
            SELECT u.id, u.username, u.avatar_url, 
                   CASE WHEN f.followed_id IS NOT NULL THEN 1 ELSE 0 END as is_followed
            FROM users u
            LEFT JOIN follows f ON u.id = f.followed_id AND f.follower_id = %s
            WHERE u.username ILIKE %s AND u.id != %s
            ORDER BY is_followed DESC, u.username ASC
            LIMIT 20;
            """
            cursor.execute(query, (user_id, f"%{search_text}%", user_id))
            return cursor.fetchall()
    except Exception as e:
        print(f"❌ Error en buscar_usuarios_para_chat: {e}")
        return []
    finally:
        release_connection(conexion)

def obtener_mensajes_paginados(user_id_1, user_id_2, limit, offset):
    conexion = get_connection()
    if not conexion:
        return []
    try:
        with conexion.cursor() as cursor:
            query = """
            SELECT sender_id, receiver_id, content, created_at
            FROM messages
            WHERE (sender_id = %s AND receiver_id = %s)
               OR (sender_id = %s AND receiver_id = %s)
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s;
            """
            cursor.execute(query, (user_id_1, user_id_2, user_id_2, user_id_1, limit, offset))
            return cursor.fetchall()
    except Exception as e:
        print(f"❌ Error en obtener_mensajes_paginados: {e}")
        return []
    finally:
        release_connection(conexion)

def insertar_mensaje(sender_id, receiver_id, content):
    conexion = get_connection()
    if not conexion:
        return None
    try:
        with conexion.cursor() as cursor:
            query = """
            INSERT INTO messages (sender_id, receiver_id, content)
            VALUES (%s, %s, %s) RETURNING id, created_at;
            """
            cursor.execute(query, (sender_id, receiver_id, content))
            resultado = cursor.fetchone()
            conexion.commit() # Aseguramos guardar en DB
            return resultado
    except Exception as e:
        print(f"❌ Error en insertar_mensaje: {e}")
        conexion.rollback()
        return None
    finally:
        release_connection(conexion)