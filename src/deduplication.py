from math import radians, sin, cos, sqrt, atan2

EARTH_RADIUS_METERS = 6_371_000

def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distância geodésica aproximada entre dois pontos."""
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_METERS * atan2(sqrt(a), sqrt(1 - a))

def find_possible_duplicate(record: dict, accepted: list[dict], radius_meters: float) -> str | None:
    lat, lon = float(record["latitude"]), float(record["longitude"])
    for previous in accepted:
        distance = haversine_meters(
            lat, lon, float(previous["latitude"]), float(previous["longitude"])
        )
        if distance <= radius_meters:
            return str(previous["id"])
    return None
