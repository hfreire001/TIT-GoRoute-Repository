# negocio/chat_service.py
from datos import chat_repo

def obtener_chats_recientes(user_id):
    # La conexión y el cursor ya se manejan dentro de chat_repo.obtener_lista_chats
    chats = chat_repo.obtener_lista_chats(user_id) 
    return [{"user_id": c[0], "username": c[1], "avatar": c[2], "last_message": c[3], "date": c[4]} for c in chats]

def buscar_usuarios_activos(user_id, search_text):
    if not search_text:
        return []
    
    # Hemos quitado el parámetro 'cursor'
    usuarios = chat_repo.buscar_usuarios_para_chat(user_id, search_text)
    return [{"user_id": u[0], "username": u[1], "avatar": u[2], "is_followed": bool(u[3])} for u in usuarios]

def obtener_historial_chat(user_id_1, user_id_2, offset=0, limit=50):
    mensajes_crudos = chat_repo.obtener_mensajes_paginados(user_id_1, user_id_2, limit, offset)
    mensajes = [{"sender_id": m[0], "receiver_id": m[1], "content": m[2], "date": m[3]} for m in mensajes_crudos]
    return mensajes[::-1] # Invertimos para que el más nuevo salga abajo

def enviar_mensaje(sender_id, receiver_id, content):
    # El commit ya lo hace chat_repo.insertar_mensaje
    nuevo_msg = chat_repo.insertar_mensaje(sender_id, receiver_id, content)
    return nuevo_msg