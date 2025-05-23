from datetime import datetime, timedelta, timezone


class AlertManager:
    """Gestiona la creación y registro de alertas."""
    def __init__(self, db_manager, geo_utils):
        self.db = db_manager
        self.geo = geo_utils

    def alertar_dueño(self, animal):
        """Envía una alerta al dueño del animal."""
        dueño = self.db.dueños.find_one({"_id": animal["idDueño"]})
        if dueño:
            mensaje = f"🔔 Alerta enviada a dueño {dueño['nombre']} {dueño['apellido']} - Animal {animal['_id']} está fuera del campo."
            print(mensaje)
            self.registrar_alerta_animal(animal, "fuera_geocerca", "Animal fuera de la geocerca.")
        else:
            print(f"⚠️ No se encontró dueño para el animal {animal['_id']}.")

    def alertar_usuarios_cercanos(self, animal):
        """Envía alertas a usuarios cercanos al animal."""
        for user in self.db.usuarios.find():
            dist = self.geo.distancia_km(animal["coordenadas"], user["coordenadas"])
            if dist <= 1:
                nivel = "🚨 ALERTA CRÍTICA" if dist <= 0.5 else "⚠️ Alerta"
                mensaje = f"{nivel} - Usuario {user['_id']} está a {dist:.2f}km del animal {animal['_id']}"
                print(mensaje)

                tipo_alerta = "animal_usuario_peligro" if dist <= 0.5 else "animal_usuario"
                mensaje_alerta = "Animal en cercanía peligrosa a Usuario" if dist <= 0.5 else "Animal en cercanía a Usuario"

                # Verificar si se debe enviar la alerta (cada 5 min)
                if self.debe_enviar_alerta_usuario(animal["_id"], user["_id"], tipo_alerta):
                     self.registrar_alerta_usuario(animal, user, tipo_alerta, mensaje_alerta)


    def registrar_alerta_animal(self, animal, tipo, mensaje):
        """Registra una alerta relacionada con un animal en MongoDB."""
        alerta = {
            "animalId": animal["_id"],
            "tipo": tipo,
            "mensaje": mensaje,
            "ubicacion": animal["coordenadas"],
            "timestamp": datetime.now(timezone.utc)
        }
        self.db.alertas.insert_one(alerta)

    def registrar_alerta_usuario(self, animal, usuario, tipo, mensaje):
        """Registra una alerta relacionada con un usuario y un animal."""
        alerta = {
            "animalId": animal["_id"],
            "usuarioId": usuario["_id"],
            "tipo": tipo,
            "mensaje": mensaje,
            "ubicacionAnimal": animal["coordenadas"],
            "ubicacionUsuario": usuario["coordenadas"],
            "timestamp": datetime.now(timezone.utc)
        }
        self.db.alertas.insert_one(alerta)

    def debe_enviar_alerta(self, animal_id, tipo, minutos=5):
        """Verifica si se debe enviar una alerta según el tiempo transcurrido."""
        ultima_alerta = self.db.alertas.find_one(
            {"animalId": animal_id, "tipo": tipo},
            sort=[("timestamp", -1)]
        )
        if not ultima_alerta or (datetime.now() - ultima_alerta["timestamp"].replace(tzinfo=None)) >= timedelta(minutes=5):
            return True
        return False

    def debe_enviar_alerta_usuario(self, animal_id, user_id, tipo, minutos=5):
        """Verifica si se debe enviar una alerta a un usuario."""
        ultima_alerta = self.db.alertas.find_one(
            {"animalId": animal_id, "usuarioId": user_id, "tipo": tipo},
            sort=[("timestamp", -1)]
        )


        
        timestamp_db = ultima_alerta["timestamp"]
        if timestamp_db.tzinfo is None:
            timestamp_db = timestamp_db.replace(tzinfo=timezone.utc)

        if not ultima_alerta or (datetime.now(timezone.utc) - timestamp_db) >= timedelta(minutes=minutos):
            return True
        return False