import json
from datos.db_connection import connect, close

def guardar_ruta(user_id, nombre_ruta, descripcion, geometria_geojson):
    """Guarda una ruta en PostgreSQL utilizando la extensión PostGIS."""
    cursor = connect()
    if not cursor:
        return False
        
    conexion = cursor.connection
    
    # 🚀 Si 'descripcion' es None o no se ha escrito nada, forzamos que sea un string vacío
    descripcion = descripcion if descripcion else ""
    
    try:
        # Pasamos el diccionario de Python a un string JSON puro
        geom_str = json.dumps(geometria_geojson)
        
        # 🚀 Insertamos usando PostGIS. 
        # (He actualizado 'user_id' a 'creator_id' y añadido 'description' para que coincida con tu SQL)
        query = """
            INSERT INTO routes (creator_id, name, description, geom) 
            VALUES (%s, %s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
        """
        # Añadimos la descripción a los valores que le pasamos al execute
        cursor.execute(query, (user_id, nombre_ruta, descripcion, geom_str))
        conexion.commit()
        return True
        
    except Exception as e:
        print(f"❌ Error al guardar la ruta en PostGIS: {e}")
        conexion.rollback()
        return False
    finally:
        cursor.close()
        close(conexion)