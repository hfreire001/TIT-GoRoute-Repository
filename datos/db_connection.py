import psycopg2
import bcrypt
from psycopg2 import Error
from psycopg2.errors import UniqueViolation

def connect():
    conexion = None
    cursor = None # Inicializamos el cursor aquí para que no rompa el bloque finally
    try:
        # 1. Configuración de la conexión
        conexion = psycopg2.connect(
            host="10.26.68.50",
            port="5432",
            database="Usuario",  # Asegúrate de que no sea 'usuario' en minúscula
            user="postgres",
            password="Admin123",
            client_encoding="utf8" # <-- ESTO FUERZA A QUE HABLEN EN UTF-8
        )

        cursor = conexion.cursor()

    except UniqueViolation:
        print("⚠️ Aviso: Ese nombre de usuario o correo ya está registrado en la base de datos.")
        if conexion:
            conexion.rollback()

    except (Exception, Error) as e:
        print(f"❌ Error inesperado de la base de datos o de Python:")
        print(repr(e))
        if conexion:
            conexion.rollback()

    return cursor
            
def close(connection):
    if connection:
        connection.close()
        print("Conexión cerrada y recursos liberados.")
    