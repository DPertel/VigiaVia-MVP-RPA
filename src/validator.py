from datetime import date
from typing import Any

VALID_SEVERITIES = {"alta", "media", "baixa"}

def validate_record(row: dict[str, Any]) -> tuple[bool, str]:
    required = ("id", "data", "latitude", "longitude", "gravidade", "descricao")
    missing = [field for field in required if row.get(field) is None or str(row.get(field)).strip() == ""]
    if missing:
        return False, "Campos obrigatórios ausentes: " + ", ".join(missing)

    try:
        date.fromisoformat(str(row["data"]).strip())
    except ValueError:
        return False, "Data inválida; use AAAA-MM-DD"

    try:
        lat = float(row["latitude"])
        lon = float(row["longitude"])
    except (TypeError, ValueError):
        return False, "Latitude/longitude devem ser numéricas"

    if not -90 <= lat <= 90:
        return False, "Latitude fora do intervalo permitido"
    if not -180 <= lon <= 180:
        return False, "Longitude fora do intervalo permitido"

    severity = str(row["gravidade"]).strip().lower()
    if severity not in VALID_SEVERITIES:
        return False, "Gravidade inválida; use alta, media ou baixa"

    return True, ""
