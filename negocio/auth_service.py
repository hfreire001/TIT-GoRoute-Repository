import bcrypt
from datos import user_repo

def verificar_login(username, password_plana):
    """
    Comprueba si el usuario existe y si la contraseña es correcta.
    Devuelve (True, datos_usuario) o (False, mensaje_error).
    """
    usuario_db = user_repo.conseguir_usuario(username)
    
    if not usuario_db:
        return False, "Usuario no encontrado."
    
    user_id, db_username, db_password_hash = usuario_db
    
    try:
        #PARA LA PREUEBA
        # Comparamos la contraseña directamente en texto plano
        if password_plana == db_password_hash:
            datos_usuario = {"id": user_id, "username": db_username}
            return True, datos_usuario
        else:
            return False, "Contraseña incorrecta."
        
        #if bcrypt.checkpw(password_plana.encode('utf-8'), db_password_hash.encode('utf-8')):
            #datos_usuario = {"id": user_id, "username": db_username}
            #return True, datos_usuario
        #else:
            #return False, "Contraseña incorrecta."
            
    except Exception as e:
        print(f"Error al verificar hash: {e}")
        return False, "Error interno del servidor."

def registrar_usuario(username, email, password_plana):
    """
    Encripta la contraseña y pide a la capa de datos que guarde el usuario.
    """
    # 1. Encriptamos la contraseña con bcrypt
    sal = bcrypt.gensalt()
    hash_pass = bcrypt.hashpw(password_plana.encode('utf-8'), sal).decode('utf-8')
    
    # 2. Se lo pasamos a la base de datos
    exito = user_repo.crear_usuario(username, email, hash_pass)
    
    if exito:
        return True, "✅ ¡Usuario registrado con éxito! Ya puedes iniciar sesión."
    else:
        return False, "⚠️ Ese usuario o correo ya está registrado en Plan&Go."