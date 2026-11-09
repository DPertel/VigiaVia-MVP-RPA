def classify_priority(severity: str) -> str:
    """Mapeia a gravidade declarada para uma fila de prioridade."""
    mapping = {"alta": "ALTA", "media": "MEDIA", "baixa": "BAIXA"}
    try:
        return mapping[severity.strip().lower()]
    except (AttributeError, KeyError):
        raise ValueError(f"Gravidade sem regra de prioridade: {severity!r}")
