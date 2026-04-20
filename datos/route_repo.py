import json
import os
import hashlib
from datos.db_connection import connect, close

def guardar_ruta(user_id, username, nombre_ruta, descripcion, geometria_geojson, imagen_file):
    """Guarda una ruta en PostGIS y procesa la imagen de portada si existe."""
    cursor = connect()
    if not cursor:
        return False
        
    conexion = cursor.connection
    descripcion = descripcion if descripcion else ""
    
    try:
        geom_str = json.dumps(geometria_geojson)
        
        # 1. INSERTAMOS LA RUTA Y PEDIMOS QUE NOS DEVUELVA EL ID GENERADO
        query = """
            INSERT INTO routes (creator_id, name, description, geom) 
            VALUES (%s, %s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
            RETURNING id;
        """
        cursor.execute(query, (user_id, nombre_ruta, descripcion, geom_str))
        
        # Obtenemos el ID de la ruta recién creada
        ruta_id = cursor.fetchone()[0] 
        
        # 2. GESTIÓN DE LA IMAGEN (Si el usuario ha subido una)
        if imagen_file is not None:
            
            # Sacamos la extensión (.png, .jpg...)
            extension = imagen_file.name.split('.')[-1].lower()
            nombre_imagen = f"{ruta_id}.{extension}"
            
            # Creamos la ruta del directorio: imagenes / hash / rutas
            directorio_destino = os.path.join("imagenes", user_id, "rutas")
            os.makedirs(directorio_destino, exist_ok=True) # Crea las carpetas si no existen
            
            # Ruta final física del archivo
            ruta_fisica = os.path.join(directorio_destino, nombre_imagen)
            
            # Guardamos la imagen en el disco duro
            with open(ruta_fisica, "wb") as f:
                f.write(imagen_file.getbuffer())
                
            # 3. ACTUALIZAMOS LA BASE DE DATOS CON LA URL DE LA IMAGEN
            # Guardamos la ruta relativa para poder cargarla luego en la web
            ruta_web = f"imagenes/{hash_usuario}/rutas/{nombre_imagen}"
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