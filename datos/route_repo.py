import json
from datos.db_connection import connect, close

def guardar_ruta(user_id, nombre_ruta, geometria_geojson):
    """Guarda una ruta en PostgreSQL utilizando la extensión PostGIS."""
    cursor = connect()
    if not cursor:
        return False
        
    conexion = cursor.connection
    try:
        # Pasamos el diccionario de Python a un string JSON puro
        geom_str = json.dumps(geometria_geojson)
        
        # Insertamos usando PostGIS. El 4326 es el sistema de coordenadas estándar (WGS84)
        query = """
            INSERT INTO routes (user_id, name, geom) 
            VALUES (%s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
        """
        cursor.execute(query, (user_id, nombre_ruta, geom_str))
        conexion.commit()
        return True
        
    except Exception as e:
        print(f"❌ Error al guardar la ruta en PostGIS: {e}")
        conexion.rollback()
        return False
    finally:
        cursor.close()
        close(conexion)