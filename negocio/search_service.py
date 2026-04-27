import os
from datos import search_repo

def get_explore_logic(seleccionados):
    if not seleccionados:
        return "tendencias", process_results_raw(search_repo.get_top_liked_routes())

    results_raw = search_repo.search_routes_by_tags(seleccionados)
    
    if not results_raw:
        return "nada", process_results_raw(search_repo.get_top_liked_routes())

    rutas_puntuadas = []
    buscados_set = {t.lower().strip() for t in seleccionados}
    num_buscado = len(buscados_set)

    for r in results_raw:
        # r[0]=id, r[1]=name, r[2]=creator_id, r[3]=tags, r[4]=username
        r_id, r_name, creator_id, tags_array, username = r[0], r[1], r[2], r[3], r[4]
        
        tags_ruta_set = set([t.lower().strip() for t in (tags_array if tags_array else [])])
        coincidencias = buscados_set.intersection(tags_ruta_set)

        rutas_puntuadas.append({
            "id": r_id,
            "nombre": r_name,
            "creator_id": creator_id,
            "username": username, # <--- Nuevo
            "match_count": len(coincidencias),
            "total_count": len(tags_ruta_set),
            "miniatura": buscar_foto_real(creator_id, r_id)
        })

    # Clasificación (exactas, contiene, sugerencias...)
    exactas = [r for r in rutas_puntuadas if r['match_count'] == num_buscado and r['total_count'] == num_buscado]
    contiene = [r for r in rutas_puntuadas if r['match_count'] == num_buscado and r['total_count'] > num_buscado]
    sugerencias = [r for r in rutas_puntuadas if r['match_count'] < num_buscado]
    sugerencias.sort(key=lambda x: x['match_count'], reverse=True)

    if exactas or contiene: return "exito", exactas + contiene
    if sugerencias: return "no_exacto_pero_sugerencias", sugerencias
    return "nada", process_results_raw(search_repo.get_top_liked_routes())

def buscar_foto_real(creator_id, route_id):
    # Ajustado para buscar por route_id como nombre de archivo
    base_path = f"C:\\Users\\garaz\\OneDrive\\Escritorio\\UNIVERSIDAD\\Cuarto\\TAP\\Plan&Go\\imagenes\\{creator_id}\\rutas\\{route_id}"
    for ext in ['jpg', 'png', 'jpeg', 'webp']:
        full_path = f"{base_path}.{ext}"
        if os.path.exists(full_path):
            return f"imagenes/{creator_id}/rutas/{route_id}.{ext}"
    return None

def process_results_raw(raw_data):
    processed = []
    for r in raw_data:
        # r[0]=id, r[1]=name, r[2]=creator_id, r[3]=likes, r[4]=username
        processed.append({
            "id": r[0],
            "nombre": r[1],
            "creator_id": r[2],
            "username": r[4], # <--- Nuevo
            "miniatura": buscar_foto_real(r[2], r[0])
        })
    return processed