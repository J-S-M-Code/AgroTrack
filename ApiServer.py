from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS


class ApiServer:
    """Gestiona la API REST con Flask."""
    def __init__(self, db_manager):
        self.app = Flask(__name__)
        CORS(self.app)
        self.db = db_manager
        self.setup_routes()

    def setup_routes(self):
        """Configura todas las rutas de la API."""
        # --- GET ---
        self.app.route("/api/duenos", methods=["GET"])(self.get_duenos)
        self.app.route("/api/duenos/<string:dueno_id>", methods=["GET"])(self.get_dueno_by_id)
        self.app.route("/api/animales", methods=["GET"])(self.get_animales)
        self.app.route("/api/animales/<string:animal_id>", methods=["GET"])(self.get_animal_by_id)
        self.app.route("/api/usuarios", methods=["GET"])(self.get_usuarios)
        self.app.route("/api/usuarios/<string:usuario_id>", methods=["GET"])(self.get_usuario_by_id)
        self.app.route("/api/campos", methods=["GET"])(self.get_campos)
        self.app.route("/api/campos/<string:campo_id>", methods=["GET"])(self.get_campo_by_id)
        self.app.route("/api/notificaciones", methods=["GET"])(self.obtener_notificaciones)

        # --- POST ---
        self.app.route("/api/duenos", methods=["POST"])(self.crear_dueno)
        self.app.route("/api/animales", methods=["POST"])(self.crear_animal)
        self.app.route("/api/campos", methods=["POST"])(self.crear_campo)
        self.app.route("/api/usuarios", methods=["POST"])(self.crear_usuario)

        # --- PUT ---
        self.app.route("/api/duenos/<string:dueno_id>", methods=["PUT"])(self.actualizar_dueno)
        self.app.route("/api/animales/<string:animal_id>", methods=["PUT"])(self.actualizar_animal)
        self.app.route("/api/campos/<string:campo_id>", methods=["PUT"])(self.actualizar_campo)
        self.app.route("/api/usuarios/<string:usuario_id>", methods=["PUT"])(self.actualizar_usuario)

        # --- DELETE ---
        self.app.route("/api/duenos/<string:dueno_id>", methods=["DELETE"])(self.eliminar_dueno)
        self.app.route("/api/animales/<string:animal_id>", methods=["DELETE"])(self.eliminar_animal)
        self.app.route("/api/campos/<string:campo_id>", methods=["DELETE"])(self.eliminar_campo)
        self.app.route("/api/usuarios/<string:usuario_id>", methods=["DELETE"])(self.eliminar_usuario)

    # --- Métodos GET ---
    def get_duenos(self):
        duenos_list = list(self.db.dueños.find({}))
        return jsonify(duenos_list)

    def get_dueno_by_id(self, dueno_id):
        dueno = self.db.dueños.find_one({"_id": dueno_id})
        return jsonify(dueno) if dueno else (jsonify({"error": "Dueño no encontrado"}), 404)

    def get_animales(self):
        animales_list = list(self.db.animales.find({}))
        return jsonify(animales_list)

    def get_animal_by_id(self, animal_id):
        animal = self.db.animales.find_one({"_id": animal_id})
        return jsonify(animal) if animal else (jsonify({"error": "Animal no encontrado"}), 404)

    def get_usuarios(self):
        usuarios_list = list(self.db.usuarios.find({}))
        return jsonify(usuarios_list)

    def get_usuario_by_id(self, usuario_id):
        usuario = self.db.usuarios.find_one({"_id": usuario_id})
        return jsonify(usuario) if usuario else (jsonify({"error": "Usuario no encontrado"}), 404)

    def get_campos(self):
        campos_list = list(self.db.campos.find({}))
        return jsonify(campos_list)

    def get_campo_by_id(self, campo_id):
        campo = self.db.campos.find_one({"_id": campo_id})
        return jsonify(campo) if campo else (jsonify({"error": "Campo no encontrado"}), 404)

    def obtener_notificaciones(self):
        alertas_list = list(self.db.alertas.find().sort("timestamp", -1).limit(10))
        resultado = []
        for alerta in alertas_list:
            resultado.append({
                "mensaje": alerta.get("mensaje", "Sin mensaje"),
                "timestamp": alerta.get("timestamp", datetime.now()).isoformat(),
                "_id": str(alerta.get("_id"))
            })
        return jsonify(resultado)

    # --- Métodos POST ---
    def crear_dueno(self):
        datos = request.get_json()
        if not datos or "_id" not in datos or "nombre" not in datos or "apellido" not in datos:
            return jsonify({"error": "Faltan campos obligatorios (_id, nombre, apellido)"}), 400
        if self.db.dueños.find_one({"_id": datos["_id"]}):
            return jsonify({"error": "Ya existe un dueño con este ID"}), 409
        try:
            self.db.dueños.insert_one(datos)
            return jsonify({"mensaje": "Dueño creado", "_id": datos["_id"]}), 201
        except Exception as e:
            return jsonify({"error": f"Error: {str(e)}"}), 500

    def crear_animal(self):
        datos = request.get_json()
        if not datos or "_id" not in datos or "coordenadas" not in datos:
            return jsonify({"error": "Faltan campos obligatorios (_id, coordenadas)"}), 400
        if self.db.animales.find_one({"_id": datos["_id"]}):
            return jsonify({"error": "Ya existe un animal con este ID"}), 409
        try:
            self.db.animales.insert_one(datos)
            return jsonify({"mensaje": "Animal creado", "_id": datos["_id"]}), 201
        except Exception as e:
            return jsonify({"error": f"Error: {str(e)}"}), 500

    def crear_campo(self):
        datos = request.get_json()
        if not datos or "_id" not in datos or "poligono" not in datos:
            return jsonify({"error": "Faltan campos obligatorios (_id, poligono)"}), 400
        if self.db.campos.find_one({"_id": datos["_id"]}):
            return jsonify({"error": "Ya existe un campo con este ID"}), 409
        try:
            self.db.campos.insert_one(datos)
            return jsonify({"mensaje": "Campo creado", "_id": datos["_id"]}), 201
        except Exception as e:
            return jsonify({"error": f"Error: {str(e)}"}), 500

    def crear_usuario(self):
        datos = request.get_json()
        if not datos or "_id" not in datos or "coordenadas" not in datos:
            return jsonify({"error": "Faltan campos obligatorios (_id, coordenadas)"}), 400
        if self.db.usuarios.find_one({"_id": datos["_id"]}):
            return jsonify({"error": "Ya existe un usuario con este ID"}), 409
        try:
            self.db.usuarios.insert_one(datos)
            return jsonify({"mensaje": "Usuario creado", "_id": datos["_id"]}), 201
        except Exception as e:
            return jsonify({"error": f"Error: {str(e)}"}), 500

    # --- Métodos PUT ---
    def actualizar_dueno(self, dueno_id):
        datos = request.get_json()
        if not datos: return jsonify({"error": "No hay datos"}), 400
        update_data = {k: v for k, v in datos.items() if k != "_id"}
        try:
            result = self.db.dueños.update_one({"_id": dueno_id}, {"$set": update_data})
            return jsonify({"mensaje": "Dueño actualizado"}) if result.matched_count else (jsonify({"error": "Dueño no encontrado"}), 404)
        except Exception as e:
            return jsonify({"error": f"Error: {str(e)}"}), 500

    def actualizar_animal(self, animal_id):
        datos = request.get_json()
        if not datos: return jsonify({"error": "No hay datos"}), 400
        update_data = {k: v for k, v in datos.items() if k != "_id"}
        try:
            result = self.db.animales.update_one({"_id": animal_id}, {"$set": update_data})
            return jsonify({"mensaje": "Animal actualizado"}) if result.matched_count else (jsonify({"error": "Animal no encontrado"}), 404)
        except Exception as e:
            return jsonify({"error": f"Error: {str(e)}"}), 500

    def actualizar_campo(self, campo_id):
        datos = request.get_json()
        if not datos: return jsonify({"error": "No hay datos"}), 400
        update_data = {k: v for k, v in datos.items() if k != "_id"}
        try:
            result = self.db.campos.update_one({"_id": campo_id}, {"$set": update_data})
            return jsonify({"mensaje": "Campo actualizado"}) if result.matched_count else (jsonify({"error": "Campo no encontrado"}), 404)
        except Exception as e:
            return jsonify({"error": f"Error: {str(e)}"}), 500

    def actualizar_usuario(self, usuario_id):
        datos = request.get_json()
        if not datos: return jsonify({"error": "No hay datos"}), 400
        update_data = {k: v for k, v in datos.items() if k != "_id"}
        try:
            result = self.db.usuarios.update_one({"_id": usuario_id}, {"$set": update_data})
            return jsonify({"mensaje": "Usuario actualizado"}) if result.matched_count else (jsonify({"error": "Usuario no encontrado"}), 404)
        except Exception as e:
            return jsonify({"error": f"Error: {str(e)}"}), 500

    # --- Métodos DELETE ---
    def eliminar_dueno(self, dueno_id):
        try:
            result = self.db.dueños.delete_one({"_id": dueno_id})
            return jsonify({"mensaje": "Dueño eliminado"}) if result.deleted_count else (jsonify({"error": "Dueño no encontrado"}), 404)
        except Exception as e:
            return jsonify({"error": f"Error: {str(e)}"}), 500

    def eliminar_animal(self, animal_id):
        try:
            result = self.db.animales.delete_one({"_id": animal_id})
            return jsonify({"mensaje": "Animal eliminado"}) if result.deleted_count else (jsonify({"error": "Animal no encontrado"}), 404)
        except Exception as e:
            return jsonify({"error": f"Error: {str(e)}"}), 500

    def eliminar_campo(self, campo_id):
        try:
            result = self.db.campos.delete_one({"_id": campo_id})
            return jsonify({"mensaje": "Campo eliminado"}) if result.deleted_count else (jsonify({"error": "Campo no encontrado"}), 404)
        except Exception as e:
            return jsonify({"error": f"Error: {str(e)}"}), 500

    def eliminar_usuario(self, usuario_id):
        try:
            result = self.db.usuarios.delete_one({"_id": usuario_id})
            return jsonify({"mensaje": "Usuario eliminado"}) if result.deleted_count else (jsonify({"error": "Usuario no encontrado"}), 404)
        except Exception as e:
            return jsonify({"error": f"Error: {str(e)}"}), 500

    def run(self, debug=False):
        """Inicia el servidor Flask."""
        self.app.run(debug=debug, use_reloader=False) # use_reloader=False es importante con hilos