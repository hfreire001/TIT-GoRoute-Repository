# negocio/search_service.py
import os
from datos import search_repo
from datos import user_repo # Importamos el user_repo para buscar usuarios

def buscar_foto_real(creator_id, route_id):
    """
    Busca la miniatura siguiendo la estructura: imagenes/{creator_id}/rutas/{route_id}.ext
    """
    base_folder = "imagenes" 
    
    for ext in ['jpg', 'png', 'jpeg', 'webp']:
        relative_path = os.path.join(base_folder, str(creator_id), "rutas", f"{route_id}.{ext}")
        
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
        return "nada", process_results_raw(search_repo.get_top_liked_routes())

    rutas_puntuadas = []
    buscados_set = {t.lower().strip() for t in seleccionados}
    num_buscado = len(buscados_set)

    for r in results_raw:
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
            "miniatura": buscar_foto_real(r['creator_id'], r['id'])
        })

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
            processed.append({
                "id": r[0],
                "nombre": r[1],
                "creator_id": r[2],
                "username": r[4] if len(r) > 4 else "Usuario",
                "likes": r[3] if len(r) > 3 else 0,
                "miniatura": buscar_foto_real(r[2], r[0])
            })
    return processed

# ---------- Refactorizado para usar el Repositorio ----------
def buscar_usuarios(nombre_buscado):
    """Llama al repositorio para mantener la arquitectura de 3 capas limpia."""
    # LLamamos a la función que ya preparamos en user_repo.py
    resultados_crudos = user_repo.buscar_usuarios_por_filtro(nombre_buscado)
    
    # Formateamos el resultado de las tuplas (id, username, avatar_url) a diccionarios
    resultados = []
    for fila in resultados_crudos:
        resultados.append({
            "id": fila[0],
            "username": fila[1],
            "avatar_url": fila[2],
            "bio": "" # La función del repo no traía bio, la dejamos vacía o la añades a user_repo
        })
    return resultados