# geolocalisation.py
import math
from typing import Optional
import lbc

# Coordonnées GPS de référence de l'UTC de Compiègne (Centre Pierre Guillaumat)
UTC_LAT = 49.40148
UTC_LON = 2.79493

def calculer_distance_utc(ad: lbc.Ad) -> Optional[float]:
    """
    Calcule la distance en kilomètres entre l'annonce et l'UTC de Compiègne.
    Retourne None si les coordonnées de l'annonce sont absentes.
    """
    lat = getattr(ad, "lat", None)
    lng = getattr(ad, "lng", None)

    # Récupération de repli si la structure de localisation est imbriquée
    if lat is None or lng is None:
        location = getattr(ad, "location", None)
        if location:
            if isinstance(location, dict):
                lat = location.get("lat")
                lng = location.get("lng")
            else:
                lat = getattr(location, "lat", None)
                lng = getattr(location, "lng", None)

    if lat is None or lng is None:
        return None

    try:
        lat = float(lat)
        lng = float(lng)
    except (ValueError, TypeError):
        return None

    # Formule de Haversine
    R = 6371.0  # Rayon moyen de la Terre en km
    dlat = math.radians(lat - UTC_LAT)
    dlng = math.radians(lng - UTC_LON)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(UTC_LAT)) * math.cos(math.radians(lat)) *
         math.sin(dlng / 2) ** 2)
    
    c = 2 * math.asin(math.sqrt(a))
    distance = R * c

    return round(distance, 2)