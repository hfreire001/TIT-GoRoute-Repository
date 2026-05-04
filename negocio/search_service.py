# negocio/search_service.py
import os
from datos import search_repo
from datos import user_repo # Importamos el user_repo para buscar usuarios

import streamlit as st

# En vez de devolver la ruta para el HTML, úsala directamente en Streamlit
def buscar_foto_real(creator_id, route_id):
    # Usa el directorio de trabajo actual (donde ejecutas streamlit run)
    base_folder = os.path.join(os.getcwd(), "imagenes")
    
    for ext in ['jpg', 'png', 'jpeg', 'webp']:
        ruta = os.path.join(base_folder, str(creator_id), "rutas", f"{route_id}.{ext}")
        if os.path.exists(ruta):
            return ruta  # ruta absoluta de disco, get_image_base64 la puede leer
            
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
            # Si llegan tuplas crudas, las mapeamos a los índices correctos:
            # [0]=id, [1]=name, [2]=creator_id, [3]=username, [4]=likes, [5]=comentarios, [6]=guardados
            processed.append({
                "id": r[0],
                "nombre": r[1],
                "creator_id": r[2],
                "username": r[3] if len(r) > 3 else "Usuario",
                "likes": r[4] if len(r) > 4 else 0,
                "comentarios": r[5] if len(r) > 5 else 0,
                "guardados": r[6] if len(r) > 6 else 0,
                "miniatura": buscar_foto_real(r[2], r[0])
            })
    return processed

# ---------- Refactorizado para usar el Repositorio ----------
def buscar_usuarios(nombre_buscado):
    """
    Capa de Negocio: Transforma los datos crudos del repo en diccionarios.
    """
    # 1. Llamamos a la NUEVA función del repositorio
    resultados_crudos = user_repo.buscar_usuarios_por_nombre(nombre_buscado)
    
    # 2. Preparamos la lista para la vista
    resultados_formateados = []
    
    if resultados_crudos:
        # Ahora 'fila' sí será una tupla real: (id, username, avatar_url, bio)
        for fila in resultados_crudos:
            resultados_formateados.append({
                "id": fila[0],          
                "username": fila[1],
                "foto": fila[2],        # El frontend busca u.get("foto")
                "bio": fila[3]          # El frontend busca u.get("bio")
            })
        
    return resultados_formateados