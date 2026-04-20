import os
from datos import search_repo

def get_explore_logic(seleccionados):
    """
    Lógica de exploración optimizada para columnas de tipo ARRAY (text[]).
    """
    if not seleccionados:
        return "tendencias", process_results_raw(search_repo.get_top_liked_routes())

    # 1. Búsqueda en repositorio
    results_raw = search_repo.search_routes_by_tags(seleccionados)
    
    if not results_raw:
        return "nada", process_results_raw(search_repo.get_top_liked_routes())

    rutas_puntuadas = []
    buscados_set = {t.lower().strip() for t in seleccionados}
    num_buscado = len(buscados_set)

    for r in results_raw:
        # r[0]=id, r[1]=name, r[2]=creator_id, r[3]=tags (ya es una lista gracias a psycopg2)
        r_id, r_name, creator_id, tags_array = r[0], r[1], r[2], r[3]
        
        # Aseguramos que tratamos con una lista y limpiamos
        tags_ruta_list = [t.lower().strip() for t in (tags_array if tags_array else [])]
        tags_ruta_set = set(tags_ruta_list)
        
        # Cálculo de relevancia
        coincidencias = buscados_set.intersection(tags_ruta_set)
        match_count = len(coincidencias)
        total_tags_ruta = len(tags_ruta_set)

        rutas_puntuadas.append({
            "id": r_id,
            "nombre": r_name,
            "creator_id": creator_id,
            "match_count": match_count,
            "total_count": total_tags_ruta,
            "miniatura": buscar_foto_real(creator_id)
        })

    # 2. Clasificación
    # Prioridad 1: Coincidencia Exacta (Tiene exactamente lo que buscas y nada más)
    exactas = [r for r in rutas_puntuadas if r['match_count'] == num_buscado and r['total_count'] == num_buscado]
    
    # Prioridad 2: Contiene todo lo que buscas pero tiene más cosas
    contiene = [r for r in rutas_puntuadas if r['match_count'] == num_buscado and r['total_count'] > num_buscado]
    
    # Prioridad 3: Coincidencia parcial (Sugerencias)
    sugerencias = [r for r in rutas_puntuadas if r['match_count'] < num_buscado]
    sugerencias.sort(key=lambda x: x['match_count'], reverse=True)

    if exactas or contiene:
        return "exito", exactas + contiene
    
    if sugerencias:
        return "no_exacto_pero_sugerencias", sugerencias

    return "nada", process_results_raw(search_repo.get_top_liked_routes())

def buscar_foto_real(creator_id):
    """Busca imagen1 en la carpeta del creador."""
    base_path = f"imagenes/{creator_id}/rutas/imagen1"
    for ext in ['jpg', 'png', 'jpeg', 'webp']:
        full_path = f"{base_path}.{ext}"
        if os.path.exists(full_path):
            return full_path
    return None

def process_results_raw(raw_data):
    """Procesador para resultados tipo tuple (Top Likes)."""
    processed = []
    for r in raw_data:
        # r[0]=id, r[1]=name, r[2]=creator_id
        processed.append({
            "id": r[0],
            "nombre": r[1],
            "miniatura": buscar_foto_real(r[2])
        })
    return processed