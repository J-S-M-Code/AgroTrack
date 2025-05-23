'''
codigo encargado de actualizar la ubicacion de animales y usuarios
'''

from pymongo import MongoClient as mc
from shapely.geometry import Point, Polygon # type: ignore
from geopy.distance import geodesic
import time
from datetime import datetime, timezone

client = mc("mongodb://localhost:543/") #direccion
db = client["agroTrack"] #de donde sacamos o como se llama

#Cargamos datos
animales = db["animales"]
dueños = db["dueños"]
campos = db["campos"]
usuarios = db["usuarios"]
alertas = db["alertas"]

print("Ubicacion 0")
db.animales.update_one({"_id": "gps001"}, {"$set": {"coordenadas": {"lat": -30.001, "lon": -65.999}}})
db.usuarios.update_one({"_id": "user001"},{"$set": {"coordenadas": {"lat": -30.013, "lon": -66.005}}})

time.sleep(15)
print("Ubicacion 1")
db.animales.update_one({"_id": "gps001"}, {"$set": {"coordenadas": {"lat": -30.002, "lon": -65.999}}})
db.usuarios.update_one({"_id": "user001"},{"$set": {"coordenadas": {"lat": -30.0085, "lon": -65.996}}})


time.sleep(15)
print("Ubicacion 2")
db.animales.update_one({"_id": "gps001"}, {"$set": {"coordenadas": {"lat": -30.005, "lon": -65.999}}})
db.usuarios.update_one({"_id": "user001"},{"$set": {"coordenadas": {"lat": -30.0085, "lon": -65.996}}})


time.sleep(15)
print("Ubicacion 3")
db.animales.update_one({"_id": "gps001"}, {"$set": {"coordenadas": {"lat": -30.003, "lon": -65.999}}})
db.usuarios.update_one({"_id": "user001"},{"$set": {"coordenadas": {"lat": -30.003, "lon": -65.985}}})


time.sleep(15)
print("Ubicacion 4")
db.animales.update_one({"_id": "gps001"}, {"$set": {"coordenadas": {"lat": -30.001, "lon": -65.999}}})
db.usuarios.update_one({"_id": "user001"},{"$set": {"coordenadas": {"lat": -30.001, "lon": -65.980}}})