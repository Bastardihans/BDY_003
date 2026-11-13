from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

uri = "mongodb+srv://hanpinilla_db_user:Admin_2026@cluster0.71rjuur.mongodb.net/"
client = MongoClient(uri)
db = client["ContentFlow"]

# ID de prueba para simular el ciclo de vida completo de una publicación
ID_PRUEBA = "pub_9999"

try:
    print("==========================================================")
    print("   INICIO DE OPERACIONES CRUD - CASO CONTENTFLOW (IE7/IE8)")
    print("==========================================================\n")

    # 1. CREATE (Inserción con control de duplicados - IE7, IE8)

    print("--- [1] CREATE: Insertando nueva publicación ---")
    nueva_publicacion = {
        "_id": ID_PRUEBA,
        "usuario_id": "user_94",
        "contenido": "Lanzamiento de nueva campaña interactiva sobre Inteligencia Artificial.",
        "fecha_publicacion": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "categoria": "Tecnología",
        "hashtags": ["#ia", "#innovacion"],
        "tipo": "Video"
    }

    try:
        resultado_insert = db.publicaciones.insert_one(nueva_publicacion)
        print(f"Éxito: Documento insertado con _id = '{resultado_insert.inserted_id}'")
    except DuplicateKeyError:
        print(f"Validación IE8: El documento '{ID_PRUEBA}' ya existe. Se omite duplicación.")


    # 2. READ (Lectura y verificación de integridad - IE7, IE8)

    print("\n--- [2] READ: Verificando documento recién creado ---")
    doc_creado = db.publicaciones.find_one({"_id": ID_PRUEBA})
    if doc_creado:
        print("Documento encontrado en Atlas:", doc_creado)
    else:
        print("Error: No se encontró el documento tras la inserción.")


    # 3. UPDATE (Actualización de campos y arreglos - IE7, IE8)

    print("\n--- [3] UPDATE: Actualizando contenido y agregando hashtag ---")
    resultado_update = db.publicaciones.update_one(
        {"_id": ID_PRUEBA},
        {
            "$set": {
                "contenido": "ACTUALIZADO: Campaña interactiva de IA y Ciencia de Datos.",
                "categoria": "Educación"
            },
            "$addToSet": {
                "hashtags": "#campaña2026"  # $addToSet evita hashtags duplicados (IE8)
            }
        }
    )
    print(f"Documentos coincidentes: {resultado_update.matched_count} | Modificados: {resultado_update.modified_count}")

    # Validación posterior al Update
    doc_actualizado = db.publicaciones.find_one({"_id": ID_PRUEBA}, {"_id": 1, "contenido": 1, "categoria": 1, "hashtags": 1})
    print("Estado tras actualización:", doc_actualizado)

    # 4. DELETE (Eliminación controlada y validación - IE7, IE8)

    print("\n--- [4] DELETE: Eliminando publicación de prueba ---")
    resultado_delete = db.publicaciones.delete_one({"_id": ID_PRUEBA})
    print(f"Documentos eliminados: {resultado_delete.deleted_count}")

    # Validación posterior al Delete (confirmar que no quedan registros huérfanos)
    doc_eliminado = db.publicaciones.find_one({"_id": ID_PRUEBA})
    if doc_eliminado is None:
        print(f"Validación IE8 exitosa: '{ID_PRUEBA}' fue eliminado correctamente y la base quedó limpia.")

except Exception as e:
    print("Error general en el flujo CRUD:", e)
finally:
    client.close()