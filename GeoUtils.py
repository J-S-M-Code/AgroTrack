from shapely import Point, Polygon
from geopy.distance import geodesic

class GeoUtils:
    """Proporciona funciones para cálculos geográficos."""
    @staticmethod
    def animal_dentro_del_campo(coord_animal, poligono_coords):
        """Verifica si un punto está dentro del polígono del campo."""
        punto = Point(coord_animal["lat"], coord_animal["lon"])
        poligono = Polygon([(p["lat"], p["lon"]) for p in poligono_coords])
        return poligono.contains(punto)

    @staticmethod
    def distancia_km(coord1, coord2):
        """Verifica distancia entre dos puntos (en km)."""
        punto1 = (coord1["lat"], coord1["lon"])
        punto2 = (coord2["lat"], coord2["lon"])
        return geodesic(punto1, punto2).km