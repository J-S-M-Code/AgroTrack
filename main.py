import logging
import AppRunner 

# Configuración Inicial
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

if __name__ == "__main__":
    app_runner = AppRunner.AppRunner()
    app_runner.run()