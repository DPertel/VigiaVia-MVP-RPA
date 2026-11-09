from math import radians, sin, cos, sqrt, atan2

EARTH_RADIUS_METERS = 6_371_000


def haversine_meters(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)

    a = (
        sin(dphi / 2) ** 2
        + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    )

    return 2 * EARTH_RADIUS_METERS * atan2(
        sqrt(a),
        sqrt(1 - a),
    )


def find_possible_duplicate_details(
    record: dict,
    accepted: list[dict],
    radius_meters: float,
):
    lat = float(record["latitude"])
    lon = float(record["longitude"])
    record_id = str(record.get("id", ""))

    for previous in accepted:
        # Ignora o próprio registro no histórico.
        if str(previous.get("id", "")) == record_id:
            continue

        distance = haversine_meters(
            lat,
            lon,
            float(previous["latitude"]),
            float(previous["longitude"]),
        )

        if distance <= radius_meters:
            return {
                "reference": str(previous["id"]),
                "distance_meters": round(distance, 2),
            }

    return None


def find_possible_duplicate(
    record: dict,
    accepted: list[dict],
    radius_meters: float,
) -> str | None:
    result = find_possible_duplicate_details(
        record,
        accepted,
        radius_meters,
    )

    return result["reference"] if result else None