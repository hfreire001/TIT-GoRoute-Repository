# datos/route_repo.py
import json
import os
from datos.db_connection import get_connection, release_connection

def guardar_ruta(user_id, username, nombre_ruta, descripcion, geometria_geojson, imagen_file, tags_seleccionados, waypoints):
    conexion = get_connection()
    if not conexion: 
        return False
        
    descripcion = descripcion if descripcion else ""
    
    try:
        geom_str = json.dumps(geometria_geojson)
        waypoints_str = json.dumps(waypoints)
        
        with conexion.cursor() as cursor:
            query = """
                INSERT INTO routes (creator_id, name, description, geom, tags, waypoints) 
                VALUES (%s, %s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326), %s, %s)
                RETURNING id;
            """
            cursor.execute(query, (user_id, nombre_ruta, descripcion, geom_str, tags_seleccionados, waypoints_str))
            ruta_id = cursor.fetchone()[0]  # type: ignore
            
            # Gestión de la imagen
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

        conexion.commit() # Guardamos los datos de la ruta y la URL de la imagen
        return True
        
    except Exception as e:
        print(f"❌ Error al guardar la ruta: {e}")
        conexion.rollback()
        return False
    finally:
        # Ahora SÍ es seguro poner esto, ya que devuelve la conexión al Pool sano y salvo
        release_connection(conexion)

def actualizar_ruta(route_id, nombre_ruta, descripcion, geometria_geojson, imagen_file, tags_seleccionados, user_id, waypoints):
    conexion = get_connection()
    if not conexion: 
        return False
        
    descripcion = descripcion if descripcion else ""

    try:
        geom_str = json.dumps(geometria_geojson)
        waypoints_str = json.dumps(waypoints)

        with conexion.cursor() as cursor:
            query = """
                UPDATE routes 
                SET name = %s, description = %s, geom = ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326), tags = %s, waypoints = %s
                WHERE id = %s AND creator_id = %s
            """
            cursor.execute(query, (nombre_ruta, descripcion, geom_str, tags_seleccionados, waypoints_str, route_id, user_id))

            # Gestión de la imagen en actualización
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
        release_connection(conexion)

def get_route_by_id(route_id):
    conexion = get_connection()
    if not conexion: 
        return None
        
    try:
        with conexion.cursor() as cursor:
            # MAGIA POSTGIS: 6 columnas (incluye waypoints)
            query = """
                SELECT name, description, ST_AsGeoJSON(geom), tags, ST_Length(geom::geography), waypoints 
                FROM routes WHERE id = %s
            """
            cursor.execute(query, (route_id,))
            return cursor.fetchone()
            
    except Exception as e:
        print(f"❌ Error al obtener ruta por ID: {e}")
        return None
    finally:
        release_connection(conexion)

def get_creador_ruta(route_id):
    """Consulta rápida a la BD para saber el dueño real de una ruta."""
    conexion = get_connection()
    if not conexion: 
        return None
        
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT creator_id FROM routes WHERE id = %s", (route_id,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else None
            
    except Exception as e:
        print(f"❌ Error al obtener creador: {e}")
        return None
    finally:
        release_connection(conexion)