import os
from datos import search_repo
from datos.db_connection import *

import os
from datos import search_repo
from datos.db_connection import *

def buscar_foto_real(creator_id, route_id):
    """
    Busca la miniatura siguiendo la estructura: imagenes/{creator_id}/rutas/{route_id}.ext
    """
    # Usamos rutas relativas al proyecto para evitar problemas de permisos y portabilidad
    # Si tu script se ejecuta desde la raíz, 'imagenes' debe estar en la raíz.
    base_folder = "imagenes" 
    
    # Extensiones que manejas según tu captura de pantalla
    for ext in ['jpg', 'png', 'jpeg', 'webp']:
        # Construimos la ruta: imagenes/4/rutas/15.png (por ejemplo)
        relative_path = os.path.join(base_folder, str(creator_id), "rutas", f"{route_id}.{ext}")
        
        # Verificamos si el archivo existe físicamente en el disco
        if os.path.exists(relative_path):
            return relative_path
            
    return None

def get_explore_logic(seleccionados):
    """
    Lógica de exploración mejorada para asegurar que las rutas de imagen sean correctas.
    """
    if not seleccionados:
        return "tendencias", process_results_raw(search_repo.get_top_liked_routes())

    results_raw = search_repo.search_routes_by_tags(seleccionados)
    
    if not results_raw:
        # Si no hay resultados, devolvemos tendencias como plan B
        return "nada", process_results_raw(search_repo.get_top_liked_routes())

    rutas_puntuadas = []
    buscados_set = {t.lower().strip() for t in seleccionados}
    num_buscado = len(buscados_set)

    for r in results_raw:
        # Normalización de datos
        tags_ruta_set = {t.lower().strip() for t in r.get('tags', [])}
        coincidencias = buscados_set.intersection(tags_ruta_set)
        match_count = len(coincidencias)

        rutas_puntuadas.append({
            "id": r['id'],
            "nombre": r['name'],
            "creator_id": r['creator_id'],
            "username": r.get('username', 'Usuario'),
            "likes": r.get('likes', 0),
            "comentarios": r.get('comentarios', 0),
            "guardados": r.get('guardados', 0),
            "match_count": match_count,
            "total_count": len(tags_ruta_set),
            # AQUÍ ES DONDE SE ASIGNA LA RUTA CORRECTA
            "miniatura": buscar_foto_real(r['creator_id'], r['id'])
        })

    # Clasificación por relevancia
    exactas = [r for r in rutas_puntuadas if r['match_count'] == num_buscado and r['total_count'] == num_buscado]
    contiene = [r for r in rutas_puntuadas if r['match_count'] == num_buscado and r['total_count'] > num_buscado]
    sugerencias = [r for r in rutas_puntuadas if r['match_count'] < num_buscado]
    sugerencias.sort(key=lambda x: x['match_count'], reverse=True)

    if exactas or contiene:
        return "exito", exactas + contiene
    
    if sugerencias:
        return "no_exacto_pero_sugerencias", sugerencias

    return "nada", process_results_raw(search_repo.get_top_liked_routes())

def process_results_raw(raw_data):
    """
    Procesador universal para convertir resultados del repo en 
    objetos listos para la interfaz de 'red social'.
    """
    processed = []
    for r in raw_data:
        # Manejamos tanto si r es diccionario como si es tupla (por seguridad)
        if isinstance(r, dict):
            processed.append({
                "id": r['id'],
                "nombre": r['name'],
                "creator_id": r['creator_id'],
                "username": r.get('username', 'Usuario'),
                "likes": r.get('likes', 0),
                "comentarios": r.get('comentarios', 0),
                "guardados": r.get('guardados', 0),
                "miniatura": buscar_foto_real(r['creator_id'], r['id'])
            })
        else:
            # Fallback para tuplas si el repo aún no está actualizado a RealDictCursor
            processed.append({
                "id": r[0],
                "nombre": r[1],
                "creator_id": r[2],
                "username": r[4] if len(r) > 4 else "Usuario",
                "likes": r[3] if len(r) > 3 else 0,
                "miniatura": buscar_foto_real(r[2], r[0])
            })
    return processed




# ---------- Añadido para búsqueda de usuarios ----------
def buscar_usuarios(nombre_buscado):
    """Consulta directa a la tabla 'users' con los nombres de columna reales."""
    cursor = connect()
    if not cursor:
        return []

    try:
        # 1. Cambiamos 'usuarios' por 'users'
        # 2. Cambiamos 'foto' por 'avatar_url'
        sql = """
            SELECT id, username, avatar_url, bio 
            FROM users 
            WHERE username ILIKE %s 
            LIMIT 15
        """
        cursor.execute(sql, (f"%{nombre_buscado.strip()}%",))
        
        columnas = [desc[0] for desc in cursor.description] # type: ignore
        resultados = []
        for row in cursor.fetchall():
            resultados.append(dict(zip(columnas, row)))
            
        return resultados
    except Exception as e:
        print(f"Error en búsqueda: {e}")
        return []
    finally:
        if cursor:
            cursor.close()