from geopy.distance import geodesic

animal = (-30.005, -65.999) # combinada con la de abajo 0.484Km
usuario = (-30.0085, -65.996)
#usuario = (-30.013, -66.005) 1.451KM
#usuario = (-30.003, -65.985) 0.896
#usuario = (-30.001, -65.980)

distancia = geodesic(animal, usuario).km
print(f"Distancia: {distancia:.3f} km")