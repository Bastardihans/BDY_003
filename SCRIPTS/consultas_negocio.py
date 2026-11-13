import time
from pymongo import MongoClient, DESCENDING

uri = "mongodb+srv://hanpinilla_db_user:Admin_2026@cluster0.71rjuur.mongodb.net/"
client = MongoClient(uri)
db = client["ContentFlow"]


# Identificar las 5 publicaciones de tipo Video más recientes dentro de categorías clave (Deportes, Tecnología, Música, Entretenimiento) emitidas desde 2025 en adelante.

try:
    # 1. Filtro compuesto ($and implícito, $in y $gte)
    filtro = {
        "tipo": "Video",
        "categoria": {"$in": ["Deportes", "Tecnología", "Música", "Entretenimiento"]},
        "fecha_publicacion": {"$gte": "2025-01-01T00:00:00"}
    }

    # 2. Proyección (campos relevantes para el reporte)
    proyeccion = {
        "_id": 1,
        "usuario_id": 1,
        "categoria": 1,
        "tipo": 1,
        "hashtags": 1,
        "fecha_publicacion": 1
    }

    # 3. Ejecución con ordenamiento descendente y medición de eficiencia (IE6)
    inicio = time.time()
    resultados = list(
        db.publicaciones.find(filtro, proyeccion)
        .sort("fecha_publicacion", DESCENDING)
        .limit(5)
    )
    tiempo_ms = (time.time() - inicio) * 1000

    print("=== CONSULTA 1: VIDEOS DESTACADOS POR CATEGORÍA Y FECHA ===")
    print(f"Tiempo de ejecución: {tiempo_ms:.2f} ms | Documentos retornados: {len(resultados)}\n")
    for doc in resultados:
        print(doc)

except Exception as e:
    print("Error al ejecutar la Consulta 1:", e)
finally:
    client.close()


## CONSULTA 2: Rastrear publicaciones asociadas a un hashtag estratégico (#cultura) que además contengan términos clave en su descripción (person, summer o article) para medir temáticas recurrentes. ##



uri = "mongodb+srv://hanpinilla_db_user:Admin_2026@cluster0.71rjuur.mongodb.net/"
client = MongoClient(uri)
db = client["ContentFlow"]

try:
    # 1. Filtro compuesto sobre arreglo ('hashtags') y búsqueda de patrón ('$regex')
    filtro = {
        "hashtags": "#cultura",
        "contenido": {"$regex": "person|summer|article", "$options": "i"}
    }

    # 2. Proyección de campos relevantes
    proyeccion = {
        "_id": 1,
        "categoria": 1,
        "tipo": 1,
        "hashtags": 1,
        "contenido": 1
    }

    # 3. Ejecución y medición de eficiencia (IE6)
    inicio = time.time()
    resultados = list(
        db.publicaciones.find(filtro, proyeccion)
        .limit(5)
    )
    tiempo_ms = (time.time() - inicio) * 1000

    print("=== CONSULTA 2: BÚSQUEDA POR HASHTAG Y PALABRA CLAVE EN CONTENIDO ===")
    print(f"Tiempo de ejecución: {tiempo_ms:.2f} ms | Documentos retornados: {len(resultados)}\n")
    for doc in resultados:
        print(doc)

except Exception as e:
    print("Error al ejecutar la Consulta 2:", e)
finally:
    client.close()


##CONSULTA 3 

## CONSULTA 3: Agregación para identificar a los 5 usuarios más activos por volumen de publicaciones ##

uri = "mongodb+srv://hanpinilla_db_user:Admin_2026@cluster0.71rjuur.mongodb.net/"
client = MongoClient(uri)
db = client["ContentFlow"]

try:
    # Pipeline de agregación: agrupa por usuario, cuenta publicaciones y lista categorías únicas
    pipeline = [
        {"$group": {
            "_id": "$usuario_id",
            "total_publicaciones": {"$sum": 1},
            "categorias_publicadas": {"$addToSet": "$categoria"}
        }},
        {"$sort": {"total_publicaciones": DESCENDING}},
        {"$limit": 5}
    ]

    inicio = time.time()
    resultados = list(db.publicaciones.aggregate(pipeline))
    tiempo_ms = (time.time() - inicio) * 1000

    print("\n=== CONSULTA 3: TOP 5 USUARIOS MÁS ACTIVOS ===")
    print(f"Tiempo de ejecución: {tiempo_ms:.2f} ms | Documentos retornados: {len(resultados)}\n")
    for doc in resultados:
        print(doc)

except Exception as e:
    print("Error al ejecutar la Consulta 3:", e)
finally:
    client.close()


### CONSULTA 4: Identificar publicaciones con hashtags duplicados para optimizar la estrategia de etiquetado ##

## CONSULTA 4: Agregación para identificar las 5 publicaciones con más reacciones ##

uri = "mongodb+srv://hanpinilla_db_user:Admin_2026@cluster0.71rjuur.mongodb.net/"
client = MongoClient(uri)
db = client["ContentFlow"]

try:
    # Pipeline de agregación: agrupa por publicacion_id en la colección reacciones y cuenta interacciones
    pipeline = [
        {"$group": {
            "_id": "$publicacion_id",
            "total_reacciones": {"$sum": 1}
        }},
        {"$sort": {"total_reacciones": DESCENDING}},
        {"$limit": 5}
    ]

    inicio = time.time()
    resultados = list(db.reacciones.aggregate(pipeline))
    tiempo_ms = (time.time() - inicio) * 1000

    print("\n=== CONSULTA 4: TOP 5 PUBLICACIONES CON MÁS REACCIONES ===")
    print(f"Tiempo de ejecución: {tiempo_ms:.2f} ms | Documentos retornados: {len(resultados)}\n")
    for doc in resultados:
        print(doc)

except Exception as e:
    print("Error al ejecutar la Consulta 4:", e)
finally:
    client.close()


## CONSULTA 5: Agregación con $unwind para identificar los 5 hashtags más utilizados ##

uri = "mongodb+srv://hanpinilla_db_user:Admin_2026@cluster0.71rjuur.mongodb.net/"
client = MongoClient(uri)
db = client["ContentFlow"]

try:
    # Pipeline de agregación: descompone el arreglo 'hashtags' con $unwind y cuenta ocurrencias
    pipeline = [
        {"$unwind": "$hashtags"},
        {"$group": {
            "_id": "$hashtags",
            "frecuencia": {"$sum": 1}
        }},
        {"$sort": {"frecuencia": DESCENDING}},
        {"$limit": 5}
    ]

    inicio = time.time()
    resultados = list(db.publicaciones.aggregate(pipeline))
    tiempo_ms = (time.time() - inicio) * 1000

    print("\n=== CONSULTA 5: TOP 5 HASHTAGS MÁS UTILIZADOS ===")
    print(f"Tiempo de ejecución: {tiempo_ms:.2f} ms | Documentos retornados: {len(resultados)}\n")
    for doc in resultados:
        print(doc)

except Exception as e:
    print("Error al ejecutar la Consulta 5:", e)
finally:
    client.close()