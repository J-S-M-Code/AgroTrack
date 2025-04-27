
'''
Suponemos que este script se ejecutara en remoto, y trabajaremos con notificaciones
gps para notificar a los usuarios y dueños sobre los animales.
Este alertara cuando el animal este fuera de su geocerca:
    Alerta al dueño: 
        Este recibira una notificacion de alerta.
        Se enviara informacion de que animal. (En app, se podria mostrar un mapa con el animal)
    Alerta al usuario:
        Se cuadrara que usuarios estan cerca de este animal y seran notificados.
        Esta notificacion sera enviada a 1km de distancia, con una segunda alerta cuando este a menos de 500m
'''

from pymongo import MongoClient as mc
from shapely.geometry import Point, Polygon # type: ignore
from geopy.distance import geodesic
import time
from datetime import datetime, timezone
import threading
from datetime import datetime, timedelta

# api.py
from flask import Flask, jsonify
from flask_cors import CORS

#------------------------------------------------
#Conexion con la base de datos en mongo
client = mc("mongodb://localhost:543/") #direccion
db = client["agroTrack"] #de donde sacamos o como se llama

#Peticiones para la pag
app = Flask(__name__)
CORS(app)  # permite peticiones desde tu página

#Cargamos datos
animales = db["animales"]
dueños = db["dueños"]
campos = db["campos"]
usuarios = db["usuarios"]
alertas = db["alertas"]
#------------------------------------------------

#------------------------------------------------
#api de la pagina para peticiones a la bd
@app.route("/api/animales")
def get_animales():
    animales = list(db.animales.find({}, {"_id": 0}))  # sin _id
    return jsonify(animales)

@app.route("/api/usuarios")
def get_usuarios():
    usuarios = list(db.usuarios.find({}, {"_id": 0}))
    return jsonify(usuarios)

@app.route("/api/campos")
def get_campos():
    campos = list(db.campos.find({}, {"_id": 0}))
    return jsonify(campos)

@app.route("/api/notificaciones")
def obtener_notificaciones():
    alertas = list(db.alertas.find().sort("_id", -1).limit(10))  # Últimas 10 alertas
    resultado = []
    for alerta in alertas:
        resultado.append({
            "mensaje": alerta.get("mensaje", "Sin mensaje"),
            "timestamp": alerta.get("timestamp", datetime.now()).isoformat()
        })
    return jsonify(resultado)
#------------------------------------------------

#------------------------------------------------
# Verifica si un punto está dentro del polígono del campo
def animal_dentro_del_campo(coord_animal, poligono_coords):
    punto = Point(coord_animal["lat"], coord_animal["lon"])
    poligono = Polygon([(p["lat"], p["lon"]) for p in poligono_coords])
    return poligono.contains(punto)
#------------------------------------------------

#------------------------------------------------
# Verifica distancia entre dos puntos (en km)
def distancia_km(coord1, coord2):
    punto1 = (coord1["lat"], coord1["lon"])
    punto2 = (coord2["lat"], coord2["lon"])
    return geodesic(punto1, punto2).km
#------------------------------------------------

#------------------------------------------------
# Alerta a dueño
def alertar_dueño(animal):
    dueño = dueños.find_one({"_id": animal["idDueño"]})
    print(f"🔔 Alerta enviada a dueño {dueño['nombre']} {dueño['apellido']} - Animal {animal['_id']} está fuera del campo.")


# Alerta a usuarios cercanos
def alertar_usuarios(animal):
    for user in usuarios.find():
        dist = distancia_km(animal["coordenadas"], user["coordenadas"])
        if dist <= 1:
            nivel = "🚨 ALERTA CRÍTICA" if dist <= 0.5 else "⚠️ Alerta"
            print(f"{nivel} - Usuario {user['_id']} está a {dist:.2f}km del animal {animal['_id']}")
    
#------------------------------------------------

#------------------------------------------------------------------------------------
# Registro de alerta para MongoDB
def registrar_alerta_animal(animal, tipo, mensaje):
    alerta = {
        "animalId": animal["_id"],
        "tipo": tipo,
        "mensaje": mensaje,
        "ubicacion": animal["coordenadas"],
        "timestamp": datetime.now(timezone.utc)
    }
    alertas.insert_one(alerta)

def registrar_alerta_usuario(animal, usuario, tipo, mensaje):
    alerta = {
        "animalId": animal["_id"],
        "usuarioId": usuario["_id"],
        "tipo": tipo,
        "mensaje": mensaje,
        "ubicacionAnimal": animal["coordenadas"],
        "ubicacionUsuario": usuario["coordenadas"],
        "timestamp": datetime.now(timezone.utc)
    }
    alertas.insert_one(alerta)
#------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------
# Verificación general para MongoDB
def verificar_animales():
    for animal in animales.find():
        campo = campos.find_one({"_id": animal["idCampo"]})

        if animal_dentro_del_campo(animal["coordenadas"], campo["poligono"]):
            print(f"✅ Animal {animal['_id']} está dentro del campo.")
        else:
            print(f"❌ Animal {animal['_id']} está FUERA del campo.")

            # Verificar si ya existe una alerta "fuera_geocerca" para este animal
            ultima_alerta = alertas.find_one({
                "animalId": animal["_id"],
                "tipo": "fuera_geocerca"
            })
            
            if ultima_alerta:
                # Convertir el timestamp de la alerta a datetime de Python
                tiempo_ultima_alerta = ultima_alerta["timestamp"].replace(tzinfo=None)  # Eliminar zona horaria si existe
                if datetime.now() - tiempo_ultima_alerta < timedelta(minutes=5):
                    print(f"🕑 Esperando 5 minutos para una nueva alerta del animal {animal['_id']}.")
                    continue  # Si aún no han pasado 5 minutos, no crear nueva alerta

            # Si no existe o han pasado 5 minutos, crear nueva alerta
            registrar_alerta_animal(animal, "fuera_geocerca", "Animal fuera de la geocerca.")
            alertar_dueño(animal)
            '''
            Problema, cuando se genera la alerta del animal no se esta ingresando 
            es esta parte REVISAR y a lo sumo ejecutar verificaciones con thread
            '''
            for user in usuarios.find():
                distancia = distancia_km(animal["coordenadas"], user["coordenadas"])
                print(distancia)
                if distancia <= 1:  # Si el usuario está a menos de 1 km
                    # Verificar si ya se alertó sobre este animal-usuario
                    ultima_alerta_usuario = alertas.find_one({
                        "animalId": animal["_id"],
                        "usuarioId": user["_id"],
                        "tipo": "animal_usuario"
                    })

                    if ultima_alerta_usuario:
                        # Convertir el timestamp de la alerta a datetime de Python
                        tiempo_ultima_alerta_usuario = ultima_alerta_usuario["timestamp"].replace(tzinfo=None)  # Eliminar zona horaria si existe
                        if datetime.now() - tiempo_ultima_alerta_usuario < timedelta(minutes=5):
                            print(f"🕑 Esperando 5 minutos para una nueva alerta de usuario para el animal {animal['_id']} y el usuario {user['_id']}.")
                            continue  # Si aún no han pasado 5 minutos, no crear nueva alerta

                    # Si no existe o han pasado 5 minutos, crear nueva alerta
                    alertar_usuarios(animal)
                    registrar_alerta_usuario(animal, user, "animal_usuario", "Animal en cercanía a Usuario")

                if distancia <= 0.5:  # Si el usuario está a menos de 500 metros (peligro)
                    # Verificar si ya se alertó sobre este animal-usuario con el tipo "animal_usuario_peligro"
                    ultima_alerta_peligro = alertas.find_one({
                        "animalId": animal["_id"],
                        "usuarioId": user["_id"],
                        "tipo": "animal_usuario_peligro"
                    })

                    if ultima_alerta_peligro:
                        # Convertir el timestamp de la alerta a datetime de Python
                        tiempo_ultima_alerta_peligro = ultima_alerta_peligro["timestamp"].replace(tzinfo=None)  # Eliminar zona horaria si existe
                        if datetime.now() - tiempo_ultima_alerta_peligro < timedelta(minutes=5):
                            print(f"🕑 Esperando 5 minutos para una nueva alerta de peligro para el animal {animal['_id']} y el usuario {user['_id']}.")
                            continue  # Si aún no han pasado 5 minutos, no crear nueva alerta

                    # Si no existe o han pasado 5 minutos, crear nueva alerta de peligro
                    print(f"🚨 Alerta de peligro: Animal {animal['_id']} y Usuario {user['_id']} están a menos de 500 metros.")
                    alertar_usuarios(animal)
                    registrar_alerta_usuario(animal, user, "animal_usuario_peligro", "Animal en cercanía peligrosa a Usuario")
#-------------------------------------------------------------------------------------

def iniciar_verificador():
    while True:
        print(f"🕒 Verificación a las {datetime.now().strftime('%H:%M:%S')}")
        verificar_animales()
        time.sleep(300)  # Simulando 5 minutos con 5 segundos

if __name__ == "__main__":
    # Crear hilo para verificador
    verificador_thread = threading.Thread(target=iniciar_verificador)
    verificador_thread.daemon = True  # Hace que se cierre cuando se cierre Flask
    verificador_thread.start()

    # Iniciar Flask
    app.run(debug=True)