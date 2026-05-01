import psycopg2
import bcrypt
from psycopg2 import Error
from psycopg2.errors import UniqueViolation
import streamlit as st


def connect():
    conexion = None
    cursor = None # Inicializamos el cursor aquí para que no rompa el bloque finally
    try:
        # 1. Configuración de la conexión
        conexion = psycopg2.connect(
            host="localhost",                  # <-- Antes era la IP del compañero
            port="5432",                       # El puerto sigue siendo el mismo
            database="mi_base_gis",            # <-- Antes era "Usuario"
            user="mi_usuario",                 # <-- Antes era "postgres"
            password="mi_contraseña_segura",   # <-- Antes era "Admin123"
            client_encoding="utf8"
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


