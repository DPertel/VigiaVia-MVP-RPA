
import csv
import json
import logging
import sqlite3
import uuid

from datetime import datetime, timezone
from pathlib import Path

from .config import (
    DB_PATH,
    DUPLICATE_RADIUS_METERS,
    REQUIRED_COLUMNS,
)
from .deduplication import find_possible_duplicate_details
from .logger_config import audit_event
from .priority import classify_priority
from .validator import validate_record


def notify_gui(event_callback, event, message, **details):
    """Envia eventos para a interface sem interromper o RPA."""
    if event_callback is None:
        return

    try:
        event_callback(event, message, **details)
    except Exception:
        pass


def read_input(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(
            f"Arquivo de entrada não encontrado: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("CSV vazio ou sem cabeçalho")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing:
            raise ValueError(
                "Colunas obrigatórias ausentes: "
                + ", ".join(sorted(missing))
            )

        return list(reader)


def load_database_history(db_path: Path) -> list[dict]:
    if not db_path.exists():
        return []

    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT occurrence_id, latitude, longitude
            FROM occurrences
            """
        )

        rows = cursor.fetchall()
        connection.close()

        return [
            {
                "id": str(row[0]),
                "latitude": float(row[1]),
                "longitude": float(row[2]),
            }
            for row in rows
        ]

    except sqlite3.Error:
        return []


def process_batch(
    input_path: Path,
    output_dir: Path,
    inbox_dir: Path,
    logger: logging.Logger,
    radius_meters: float = DUPLICATE_RADIUS_METERS,
    include_history: bool = False,
    db_path: Path = DB_PATH,
    event_callback=None,
) -> dict:
    execution_id = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + "-"
        + uuid.uuid4().hex[:6]
    )

    rows = read_input(input_path)

    accepted_for_dedup = []
    integration_items = []
    results = []

    counts = {
        "total": len(rows),
        "processados": 0,
        "invalidos": 0,
        "possiveis_duplicados": 0,
        "erros": 0,
    }

    if include_history:
        accepted_for_dedup.extend(
            load_database_history(db_path)
        )

    logger.info(
        "INICIO execucao=%s arquivo=%s total=%d historico=%s",
        execution_id,
        input_path.name,
        len(rows),
        include_history,
    )

    audit_event(
        logger,
        "LOTE_INICIADO",
        execution_id=execution_id,
        arquivo=input_path.name,
        total=len(rows),
        consulta_historico=include_history,
    )

    notify_gui(
        event_callback,
        "LOTE_INICIADO",
        f"Lote iniciado: {len(rows)} relatos encontrados.",
        execution_id=execution_id,
        total=len(rows),
        arquivo=input_path.name,
    )

    for index, row in enumerate(rows, start=1):
        item_id = str(row.get("id", "")).strip() or f"linha-{index}"

        notify_gui(
            event_callback,
            "ITEM_EM_ANALISE",
            f"Analisando relato {item_id} ({index}/{len(rows)}).",
            relato=item_id,
            indice=index,
            total=len(rows),
        )

        try:
            valid, reason = validate_record(row)

            if not valid:
                counts["invalidos"] += 1

                results.append({
                    "id": item_id,
                    "status": "INVALIDO",
                    "prioridade": "",
                    "referencia_duplicidade": "",
                    "motivo": reason,
                })

                logger.warning(
                    "ITEM_INVALIDO id=%s motivo=%s",
                    item_id,
                    reason,
                )

                audit_event(
                    logger,
                    "RELATO_REJEITADO",
                    execution_id=execution_id,
                    relato=item_id,
                    motivo=reason,
                )

                notify_gui(
                    event_callback,
                    "RELATO_REJEITADO",
                    f"Relato {item_id} rejeitado: {reason}",
                    relato=item_id,
                    motivo=reason,
                )

                continue

            normalized = {
                "id": item_id,
                "data": str(row["data"]).strip(),
                "latitude": round(float(row["latitude"]), 6),
                "longitude": round(float(row["longitude"]), 6),
                "gravidade": str(row["gravidade"]).strip().lower(),
                "descricao": str(row["descricao"]).strip(),
            }

            duplicate = find_possible_duplicate_details(
                normalized,
                accepted_for_dedup,
                radius_meters,
            )

            if duplicate:
                counts["possiveis_duplicados"] += 1

                distance = duplicate["distance_meters"]
                reference = duplicate["reference"]

                reason = (
                    f"Possível duplicidade: distância de {distance} m "
                    f"da ocorrência {reference}; limite configurado "
                    f"de {radius_meters:.0f} m"
                )

                results.append({
                    "id": item_id,
                    "status": "POSSIVEL_DUPLICIDADE",
                    "prioridade": "",
                    "referencia_duplicidade": reference,
                    "motivo": reason,
                })

                logger.warning(
                    "POSSIVEL_DUPLICIDADE id=%s referencia=%s distancia_m=%.2f",
                    item_id,
                    reference,
                    distance,
                )

                audit_event(
                    logger,
                    "POSSIVEL_DUPLICIDADE",
                    execution_id=execution_id,
                    relato=item_id,
                    referencia=reference,
                    distancia_metros=distance,
                    limite_metros=radius_meters,
                )

                notify_gui(
                    event_callback,
                    "POSSIVEL_DUPLICIDADE",
                    f"Relato {item_id}: possível duplicidade com "
                    f"{reference} ({distance} m).",
                    relato=item_id,
                    referencia=reference,
                    distancia_metros=distance,
                )

                continue

            priority = classify_priority(
                normalized["gravidade"]
            )

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
                "execution_id": execution_id,
            })

            counts["processados"] += 1

            reason = (
                f"Relato validado. Gravidade "
                f"{normalized['gravidade']} classificada "
                f"como prioridade {priority}."
            )

            results.append({
                "id": item_id,
                "status": "PROCESSADO",
                "prioridade": priority,
                "referencia_duplicidade": "",
                "motivo": reason,
            })

            logger.info(
                "ITEM_PROCESSADO id=%s gravidade=%s prioridade=%s",
                item_id,
                normalized["gravidade"],
                priority,
            )

            audit_event(
                logger,
                "RELATO_PROCESSADO",
                execution_id=execution_id,
                relato=item_id,
                gravidade=normalized["gravidade"],
                prioridade=priority,
                latitude=normalized["latitude"],
                longitude=normalized["longitude"],
                motivo=reason,
            )

            notify_gui(
                event_callback,
                "ITEM_PROCESSADO",
                f"Relato {item_id} processado. Prioridade: {priority}.",
                relato=item_id,
                prioridade=priority,
                gravidade=normalized["gravidade"],
            )

        except Exception as exc:
            counts["erros"] += 1

            results.append({
                "id": item_id,
                "status": "ERRO",
                "prioridade": "",
                "referencia_duplicidade": "",
                "motivo": type(exc).__name__,
            })

            logger.exception(
                "ERRO_ITEM id=%s tipo=%s",
                item_id,
                type(exc).__name__,
            )

            audit_event(
                logger,
                "ERRO_NO_RELATO",
                execution_id=execution_id,
                relato=item_id,
                tipo=type(exc).__name__,
                mensagem=str(exc),
            )

            notify_gui(
                event_callback,
                "ERRO_NO_RELATO",
                f"Erro ao processar relato {item_id}: {exc}",
                relato=item_id,
                erro=str(exc),
            )

        finally:
            notify_gui(
                event_callback,
                "ITEM_FINALIZADO",
                f"Análise do relato {item_id} finalizada.",
                relato=item_id,
                indice=index,
                total=len(rows),
            )

    output_dir.mkdir(parents=True, exist_ok=True)
    inbox_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / f"resultado_{execution_id}.csv"
    json_path = inbox_dir / f"ocorrencias_{execution_id}.json"

    with csv_path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "id",
                "status",
                "prioridade",
                "referencia_duplicidade",
                "motivo",
            ],
        )
        writer.writeheader()
        writer.writerows(results)

    payload = {
        "schema_version": "1.0",
        "execution_id": execution_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "vigiavia-rpa",
        "items": integration_items,
    }

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(
            payload,
            file,
            ensure_ascii=False,
            indent=2,
        )

    notify_gui(
        event_callback,
        "ARQUIVOS_GERADOS",
        "Relatórios CSV e JSON gerados com sucesso.",
        csv_path=str(csv_path),
        json_path=str(json_path),
    )

    logger.info(
        "FIM execucao=%s totais=%s",
        execution_id,
        counts,
    )

    audit_event(
        logger,
        "LOTE_FINALIZADO",
        execution_id=execution_id,
        totais=counts,
        arquivo_csv=str(csv_path),
        arquivo_json=str(json_path),
    )

    notify_gui(
        event_callback,
        "LOTE_FINALIZADO",
        "Análise do lote concluída.",
        execution_id=execution_id,
        counts=counts,
    )

    return {
        "execution_id": execution_id,
        "counts": counts,
        "csv_path": csv_path,
        "json_path": json_path,
    }
