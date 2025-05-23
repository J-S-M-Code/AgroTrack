from datetime import datetime
import time


class AnimalVerifier:
    """Realiza la verificación periódica del estado de los animales."""
    def __init__(self, db_manager, geo_utils, alert_manager):
        self.db = db_manager
        self.geo = geo_utils
        self.alerter = alert_manager

    def verificar_animales(self):
        """Ejecuta el ciclo de verificación para todos los animales."""
        print(f"➡️  Verificando animales...")
        for animal in self.db.animales.find():
            campo = self.db.campos.find_one({"_id": animal.get("idCampo")})

            if not campo:
                print(f"⚠️ Animal {animal['_id']} no tiene campo asignado o el campo no existe. Saltando verificación.")
                continue

            print(f"   ➡️ Verificando animal: {animal['_id']}")

            dentro = self.geo.animal_dentro_del_campo(animal["coordenadas"], campo["poligono"])

            if dentro:
                print(f"   ✅ Animal {animal['_id']} está dentro del campo.")
            else:
                print(f"   ❌ Animal {animal['_id']} está FUERA del campo.")

                # Alerta a dueño si debe enviarse
                if self.alerter.debe_enviar_alerta(animal["_id"], "fuera_geocerca"):
                    self.alerter.alertar_dueño(animal) # Ya registra la alerta

                # Alerta a usuarios cercanos
                self.alerter.alertar_usuarios_cercanos(animal) # Ya registra y verifica tiempo


    def iniciar_verificador(self):
        """Inicia el bucle de verificación continua."""
        while True:
            print(f"🕒 Verificación a las {datetime.now().strftime('%H:%M:%S')}")
            self.verificar_animales()
            time.sleep(5)  # Simulando 5 minutos con 5 segundos
            print("\n" + "-"*30 + "\n")