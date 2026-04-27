import json
import os
from datos.db_connection import connect, close

def guardar_ruta(user_id, username, nombre_ruta, descripcion, geometria_geojson, imagen_file, tags_seleccionados):
    """Guarda una ruta en PostGIS y procesa la imagen de portada si existe."""
    cursor = connect()
    if not cursor:
        return False
        
    conexion = cursor.connection
    descripcion = descripcion if descripcion else ""
    
    try:
        geom_str = json.dumps(geometria_geojson)
        
        # 1. INSERTAMOS LA RUTA CON LAS ETIQUETAS Y PEDIMOS QUE NOS DEVUELVA EL ID GENERADO
        query = """
            INSERT INTO routes (creator_id, name, description, geom, tags) 
            VALUES (%s, %s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326), %s)
            RETURNING id;
        """
        cursor.execute(query, (user_id, nombre_ruta, descripcion, geom_str, tags_seleccionados))
        
        ruta_id = cursor.fetchone()[0] 
        
        # 2. GESTIÓN DE LA IMAGEN
        if imagen_file is not None:
            extension = imagen_file.name.split('.')[-1].lower()
            nombre_imagen = f"{ruta_id}.{extension}"
            
            directorio_destino = os.path.join("imagenes", str(user_id), "rutas")
            os.makedirs(directorio_destino, exist_ok=True) 
            
            ruta_fisica = os.path.join(directorio_destino, nombre_imagen)
            
            with open(ruta_fisica, "wb") as f:
                f.write(imagen_file.getbuffer())
                
            ruta_web = f"imagenes/{user_id}/rutas/{nombre_imagen}"
            query_update = "UPDATE routes SET thumbnail_url = %s WHERE id = %s"
            cursor.execute(query_update, (ruta_web, ruta_id))

        conexion.commit()
        return True
        
    except Exception as e:
        print(f"❌ Error al guardar la ruta: {e}")
        conexion.rollback()
        return False
    finally:
        cursor.close()
        close(conexion)

# 🚀 NUEVA FUNCIÓN: Obtiene todos los detalles de una ruta para poder verla en el mapa
def get_route_by_id(route_id):
    cursor = connect()
    if not cursor: return None
    try:
        # Añadimos ST_Length para que PostGIS nos devuelva la distancia en metros
        query = """
            SELECT name, description, ST_AsGeoJSON(geom), tags, ST_Length(geom::geography) 
            FROM routes WHERE id = %s
        """
        cursor.execute(query, (route_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        close(cursor.connection)