import psycopg2
from psycopg2 import pool, Error
import streamlit as st

@st.cache_resource
def get_connection_pool():
    try:
        connection_pool = psycopg2.pool.ThreadedConnectionPool(
            1, 20,
            host="localhost",           # "localhost" funciona porque tu script está FUERA de Docker
            port="5432",                # El puerto que mapeaste en el YAML
            database="mi_base_gis",     # El valor de POSTGRES_DB en tu YAML
            user="mi_usuario",          # El valor de POSTGRES_USER en tu YAML
            password="mi_contraseña_segura", # El valor de POSTGRES_PASSWORD en tu YAML
            client_encoding="utf8"
        )
        print("✅ Pool de conexiones a la base de datos inicializado.")
        return connection_pool
    except (Exception, Error) as e:
        print(f"❌ Error al crear el pool de conexiones:")
        print(repr(e))
        return None

def get_connection():
    pool_db = get_connection_pool()
    if pool_db:
        try:
            return pool_db.getconn()
        except Exception as e:
            print(f"❌ Error al obtener conexión del pool: {repr(e)}")
            return None
    return None

def release_connection(conexion):
    pool_db = get_connection_pool()
    if pool_db and conexion:
        try:
            pool_db.putconn(conexion)
        except Exception as e:
            print(f"❌ Error al liberar la conexión: {repr(e)}")