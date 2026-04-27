# datos/db_connection.py
import psycopg2
from psycopg2 import Error
from psycopg2.errors import UniqueViolation
import streamlit as st

@st.cache_resource
def connect():
    """
    Establece y mantiene la conexión a la base de datos en caché para máxima velocidad.
    """
    conexion = None
    try:
        conexion = psycopg2.connect(
            host="10.199.150.50",
            port="5432",
            database="Usuario", 
            user="postgres",
            password="Admin123",
            client_encoding="utf8"
        )
        return conexion
    except UniqueViolation:
        print("⚠️ Aviso: Ese nombre de usuario o correo ya está registrado.")
        if conexion:
            conexion.rollback()
    except (Exception, Error) as e:
        print(f"❌ Error inesperado de la base de datos:")
        print(repr(e))
        if conexion:
            conexion.rollback()
            
    return None

# Eliminamos la función close() porque queremos que la conexión siga viva en la caché