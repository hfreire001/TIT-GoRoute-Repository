# negocio/chat_service.py
from datos import chat_repo
from datos.db_connection import get_connection # Asumiendo tu script de conexión

def obtener_chats_recientes(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    chats = chat_repo.obtener_lista_chats(user_id, cursor)
    conn.close()
    
    # Formateamos a diccionario para pasarlo a la vista
    return [{"user_id": c[0], "username": c[1], "avatar": c[2], "last_message": c[3], "date": c[4]} for c in chats]

def buscar_usuarios_activos(user_id, search_text):
    if not search_text:
        return []
        
    conn = get_connection()
    cursor = conn.cursor()
    usuarios = chat_repo.buscar_usuarios_para_chat(user_id, search_text, cursor)
    conn.close()
    
    return [{"user_id": u[0], "username": u[1], "avatar": u[2], "is_followed": bool(u[3])} for u in usuarios]

def obtener_historial_chat(user_id_1, user_id_2, offset=0, limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    mensajes_crudos = chat_repo.obtener_mensajes_paginados(user_id_1, user_id_2, limit, offset, cursor)
    conn.close()
    
    mensajes = [{"sender_id": m[0], "receiver_id": m[1], "content": m[2], "date": m[3]} for m in mensajes_crudos]
    
    # Invertimos la lista para que el mensaje más antiguo de este bloque aparezca arriba y el nuevo abajo
    return mensajes[::-1]

def enviar_mensaje(sender_id, receiver_id, content):
    conn = get_connection()
    cursor = conn.cursor()
    nuevo_msg = chat_repo.insertar_mensaje(sender_id, receiver_id, content, cursor)
    conn.commit()
    conn.close()
    return nuevo_msg