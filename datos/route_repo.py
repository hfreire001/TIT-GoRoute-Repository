import json
import os
from datos.db_connection import connect

def guardar_ruta(user_id, username, nombre_ruta, descripcion, geometria_geojson, imagen_file, tags_seleccionados, waypoints):
    cursor = connect()
    if not cursor: return False
    conexion = cursor.connection
    descripcion = descripcion if descripcion else ""
    
    try:
        geom_str = json.dumps(geometria_geojson)
        waypoints_str = json.dumps(waypoints)
        
        query = """
            INSERT INTO routes (creator_id, name, description, geom, tags, waypoints) 
            VALUES (%s, %s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326), %s, %s)
            RETURNING id;
        """
        cursor.execute(query, (user_id, nombre_ruta, descripcion, geom_str, tags_seleccionados, waypoints_str))
        ruta_id = cursor.fetchone()[0] 
        
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
        # NUNCA ponemos close(conexion) aquí para no romper la app

def actualizar_ruta(route_id, nombre_ruta, descripcion, geometria_geojson, imagen_file, tags_seleccionados, user_id, waypoints):
    cursor = connect()
    if not cursor: return False
    conexion = cursor.connection
    descripcion = descripcion if descripcion else ""

    try:
        geom_str = json.dumps(geometria_geojson)
        waypoints_str = json.dumps(waypoints)

        query = """
            UPDATE routes 
            SET name = %s, description = %s, geom = ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326), tags = %s, waypoints = %s
            WHERE id = %s AND creator_id = %s
        """
        cursor.execute(query, (nombre_ruta, descripcion, geom_str, tags_seleccionados, waypoints_str, route_id, user_id))

        if imagen_file is not None:
            extension = imagen_file.name.split('.')[-1].lower()
            nombre_imagen = f"{route_id}.{extension}"
            directorio_destino = os.path.join("imagenes", str(user_id), "rutas")
            os.makedirs(directorio_destino, exist_ok=True) 
            ruta_fisica = os.path.join(directorio_destino, nombre_imagen)
            
            with open(ruta_fisica, "wb") as f:
                f.write(imagen_file.getbuffer())
                
            ruta_web = f"imagenes/{user_id}/rutas/{nombre_imagen}"
            query_update = "UPDATE routes SET thumbnail_url = %s WHERE id = %s"
            cursor.execute(query_update, (ruta_web, route_id))

        conexion.commit()
        return True
    except Exception as e:
        print(f"❌ Error al actualizar la ruta: {e}")
        conexion.rollback()
        return False
    finally:
        cursor.close()

def get_route_by_id(route_id):
    cursor = connect()
    if not cursor: return None
    try:
        # AQUÍ ESTÁ LA MAGIA: 6 columnas (incluye waypoints)
        query = """
            SELECT name, description, ST_AsGeoJSON(geom), tags, ST_Length(geom::geography), waypoints 
            FROM routes WHERE id = %s
        """
        cursor.execute(query, (route_id,))
        return cursor.fetchone()
    finally:
        cursor.close()