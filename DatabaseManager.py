from pymongo import MongoClient as mc

class DatabaseManager:
    """Gestiona la conexión y el acceso a la base de datos MongoDB."""
    def __init__(self, db_url="mongodb://localhost:543/", db_name="agroTrack"):
        try:
            self.client = mc(db_url)
            self.db = self.client[db_name]
            self.animales = self.db["animales"]
            self.dueños = self.db["dueños"]
            self.campos = self.db["campos"]
            self.usuarios = self.db["usuarios"]
            self.alertas = self.db["alertas"]
            print("💾 Conexión a MongoDB establecida.")
        except Exception as e:
            print(f"❌ Error al conectar a MongoDB: {e}")
            exit()