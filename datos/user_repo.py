from datos.db_connection import connect, close
from psycopg2.errors import UniqueViolation
#Crear la clase de usuario
#Métodos que generan query 

def conseguir_usuario(username):
    # Busca un usuario en la BD por su nombre de usuario."
    cursor = connect()
    
    if not cursor:
        return None
        
    # Extraemos la conexión del propio cursor para poder cerrarla luego
    conexion = cursor.connection
        
    try:
        # Consulta SQL (Asegúrate de que tu tabla se llama 'users' o cámbialo aquí)
        query = "SELECT id, username, password_hash FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        return cursor.fetchone()  
            
    except Exception as e:
        print(f"❌ Error en la consulta SQL: {e}")
        return None
    finally:
        # Cerramos el cursor y usamos TU función close() pasándole la conexión
        cursor.close()
        close(conexion)

def crear_usuario(username, email, password_hash):
    """Inserta un nuevo usuario en la base de datos."""
    cursor = connect()
    if not cursor:
        return False
        
    conexion = cursor.connection
    try:
        query = "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, email, password_hash))
        conexion.commit() # ¡Guardamos los cambios en la BD!
        return True
        
    except UniqueViolation:
        # Si el usuario o correo ya existe (porque la BD tiene restricciones UNIQUE)
        conexion.rollback()
        return False
    except Exception as e:
        print(f"❌ Error insertando usuario: {e}")
        conexion.rollback()
        return False
    finally:
        cursor.close()
        close(conexion)