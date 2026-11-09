import csv
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .config import DUPLICATE_RADIUS_METERS, REQUIRED_COLUMNS
from .deduplication import find_possible_duplicate
from .priority import classify_priority
from .validator import validate_record

def read_input(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV vazio ou sem cabeçalho")
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError("Colunas obrigatórias ausentes: " + ", ".join(sorted(missing)))
        return list(reader)

def process_batch(input_path: Path, output_dir: Path, inbox_dir: Path,
                  logger: logging.Logger, radius_meters: float = DUPLICATE_RADIUS_METERS) -> dict:
    execution_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:6]
    rows = read_input(input_path)
    accepted_for_dedup: list[dict] = []
    integration_items: list[dict] = []
    results: list[dict] = []
    counts = {"total": len(rows), "processados": 0, "invalidos": 0,
              "possiveis_duplicados": 0, "erros": 0}

    logger.info("INICIO execucao=%s total=%d", execution_id, len(rows))

    # Laço obrigatório: cada registro do lote é tratado isoladamente.
    for index, row in enumerate(rows, start=1):
        item_id = str(row.get("id", "")).strip() or f"linha-{index}"
        try:
            valid, reason = validate_record(row)
            if not valid:
                counts["invalidos"] += 1
                results.append({"id": item_id, "status": "INVALIDO", "prioridade": "",
                                "referencia_duplicidade": "", "motivo": reason})
                logger.warning("ITEM_INVALIDO id=%s motivo=%s", item_id, reason)
                continue

            normalized = {
                "id": item_id,
                "data": str(row["data"]).strip(),
                "latitude": round(float(row["latitude"]), 6),
                "longitude": round(float(row["longitude"]), 6),
                "gravidade": str(row["gravidade"]).strip().lower(),
                "descricao": str(row["descricao"]).strip()
            }

            duplicate_of = find_possible_duplicate(normalized, accepted_for_dedup, radius_meters)
            if duplicate_of:
                counts["possiveis_duplicados"] += 1
                results.append({"id": item_id, "status": "POSSIVEL_DUPLICIDADE", "prioridade": "",
                                "referencia_duplicidade": duplicate_of,
                                "motivo": f"Distância dentro de {radius_meters:.0f} m"})
                logger.info("POSSIVEL_DUPLICIDADE id=%s referencia=%s", item_id, duplicate_of)
                continue

            priority = classify_priority(normalized["gravidade"])
            accepted_for_dedup.append(normalized)
            integration_items.append({
                "occurrence_id": normalized["id"],
                "occurred_at": normalized["data"],
                "latitude": normalized["latitude"],
                "longitude": normalized["longitude"],
                "severity": normalized["gravidade"],
                "priority": priority.lower(),
                "description": normalized["descricao"],
                "source": "vigiavia-rpa",
                "execution_id": execution_id
            })
            counts["processados"] += 1
            results.append({"id": item_id, "status": "PROCESSADO", "prioridade": priority,
                            "referencia_duplicidade": "", "motivo": "Validado e exportado"})
            logger.info("ITEM_PROCESSADO id=%s prioridade=%s", item_id, priority)

        except Exception as exc:  # isolamento por item: um registro não derruba o lote
            counts["erros"] += 1
            results.append({"id": item_id, "status": "ERRO", "prioridade": "",
                            "referencia_duplicidade": "", "motivo": type(exc).__name__})
            logger.exception("ERRO_ITEM id=%s tipo=%s", item_id, type(exc).__name__)

    output_dir.mkdir(parents=True, exist_ok=True)
    inbox_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / f"resultado_{execution_id}.csv"
    json_path = inbox_dir / f"ocorrencias_{execution_id}.json"

    # Saídas são gravadas após o processamento; falha de escrita não é mascarada.
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "status", "prioridade", "referencia_duplicidade", "motivo"
        ])
        writer.writeheader()
        writer.writerows(results)

    payload = {
        "schema_version": "1.0",
        "execution_id": execution_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "vigiavia-rpa",
        "items": integration_items
    }
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    logger.info("FIM execucao=%s totais=%s", execution_id, counts)
    return {"execution_id": execution_id, "counts": counts,
            "csv_path": csv_path, "json_path": json_path}
