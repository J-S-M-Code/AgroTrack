import os
import subprocess
import threading
import webbrowser

import AlertManager
import AnimalVerifier
import ApiServer
import DatabaseManager
import GeoUtils


class AppRunner:
    """Orquesta el inicio y la ejecución de la aplicación."""
    def __init__(self):
        self.db_manager = DatabaseManager.DatabaseManager()
        self.geo_utils = GeoUtils.GeoUtils()
        self.alert_manager = AlertManager.AlertManager(self.db_manager, self.geo_utils)
        self.verifier = AnimalVerifier.AnimalVerifier(self.db_manager, self.geo_utils, self.alert_manager)
        self.api_server = ApiServer.ApiServer(self.db_manager)

    def _iniciador_emuladorUbi(self):
        """Inicia el script del emulador de ubicación."""
        try:
            print("🚀 Iniciando emulador de ubicación...")
            subprocess.Popen(["python", "location emulator.py"])
            print("🛰️  Emulador iniciado.")
        except FileNotFoundError:
            print("❌ Error: No se encontró 'location emulator.py'. Asegúrate de que exista.")
        except Exception as e:
            print(f"❌ Error al iniciar el emulador: {e}")

    def _abrir_navegador(self):
        """Abre la interfaz web en el navegador."""
        try:
            ruta_index = os.path.abspath("")
            url = "file://" + os.path.join(ruta_index, "web", "index.html")
            print(f"🌍 Abriendo interfaz web en: {url}")
            webbrowser.open(url)
        except Exception as e:
            print(f"❌ Error al abrir el navegador: {e}")

    def run(self):
        """Inicia todos los componentes de la aplicación."""
        print("🏁 Iniciando AgroTrack...")

        # 1. Abrir navegador
        self._abrir_navegador()

        # 2. Iniciar emulador (hilo)
        emulador_thread = threading.Thread(target=self._iniciador_emuladorUbi)
        emulador_thread.daemon = True
        emulador_thread.start()

        # 3. Iniciar verificador (hilo)
        verificador_thread = threading.Thread(target=self.verifier.iniciar_verificador)
        verificador_thread.daemon = True
        verificador_thread.start()

        # 4. Iniciar servidor API (hilo principal)
        print("📡 Iniciando servidor API...")
        self.api_server.run(debug=False)