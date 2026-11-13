import logging
from datetime import datetime
from flask import Flask, request, jsonify
from pymongo import MongoClient, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

# 1. Configuración de Trazabilidad y Logs (IE11 / Apartado 7)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("actividad_api.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

# 2. Conexión a MongoDB Atlas (IE9)
uri = "mongodb+srv://hanpinilla_db_user:Admin_2026@cluster0.71rjuur.mongodb.net/"
try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    db = client["ContentFlow"]
    logging.info("Conexión exitosa entre API Flask y MongoDB Atlas.")
except Exception as e:
    logging.critical(f"Error crítico conectando a MongoDB Atlas: {e}")
    raise

# Endpoint 1: Health Check / Prueba de conectividad (IE11)
@app.route("/api/estado", methods=["GET"])
def verificar_estado():
    logging.info("Consulta GET /api/estado - Verificación de conectividad.")
    return jsonify({
        "estado": "en_linea",
        "base_datos": "ContentFlow",
        "timestamp": datetime.now().isoformat()
    }), 200

# Endpoint 2: Lectura en tiempo real con filtro opcional por categoría (IE9, IE10)
@app.route("/api/publicaciones", methods=["GET"])
def obtener_publicaciones():
    try:
        categoria = request.args.get("categoria")
        filtro = {"categoria": categoria} if categoria else {}
        
        publicaciones = list(
            db.publicaciones.find(filtro)
            .sort("fecha_publicacion", DESCENDING)
            .limit(5)
        )
        logging.info(f"GET /api/publicaciones | Filtro: {filtro} | Retornados: {len(publicaciones)}")
        return jsonify({
            "total_retornados": len(publicaciones),
            "datos": publicaciones
        }), 200
    except PyMongoError as e:
        logging.error(f"Error de base de datos en GET /api/publicaciones: {e}")
        return jsonify({"error": "Error interno al consultar la base de datos"}), 500

# Endpoint 3: Escritura en tiempo real con validación de entradas (IE9, IE10, IE11)
@app.route("/api/publicaciones", methods=["POST"])
def crear_publicacion():
    datos = request.get_json(silent=True)
    
    # Validación de estructura JSON y campos obligatorios (IE11)
    if not datos:
        logging.warning("POST /api/publicaciones rechazado: Cuerpo JSON vacío o inválido.")
        return jsonify({"error": "El cuerpo de la petición debe ser un JSON válido."}), 400

    campos_requeridos = ["_id", "usuario_id", "contenido", "categoria", "tipo"]
    faltantes = [campo for campo in campos_requeridos if campo not in datos or not str(datos[campo]).strip()]
    
    if faltantes:
        logging.warning(f"POST /api/publicaciones rechazado: Faltan campos {faltantes}")
        return jsonify({"error": f"Campos obligatorios faltantes o vacíos: {faltantes}"}), 400

    # Armado del documento validado
    nueva_pub = {
        "_id": str(datos["_id"]).strip(),
        "usuario_id": str(datos["usuario_id"]).strip(),
        "contenido": str(datos["contenido"]).strip(),
        "fecha_publicacion": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "categoria": str(datos["categoria"]).strip(),
        "hashtags": datos.get("hashtags", []),
        "tipo": str(datos["tipo"]).strip()
    }

    try:
        db.publicaciones.insert_one(nueva_pub)
        logging.info(f"POST /api/publicaciones exitoso: Documento '{nueva_pub['_id']}' creado.")
        return jsonify({
            "mensaje": "Publicación registrada exitosamente en tiempo real.",
            "publicacion": nueva_pub
        }), 201
    except DuplicateKeyError:
        logging.warning(f"Conflicto de duplicidad en POST: _id '{nueva_pub['_id']}' ya existe.")
        return jsonify({"error": f"Ya existe una publicación con el _id '{nueva_pub['_id']}'."}), 409
    except PyMongoError as e:
        logging.error(f"Error de MongoDB al insertar documento: {e}")
        return jsonify({"error": "No se pudo guardar el registro en la base de datos."}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)