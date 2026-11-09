
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logger(log_path: Path) -> logging.Logger:
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("vigiavia")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    main_handler = RotatingFileHandler(
        log_path,
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    main_handler.setFormatter(formatter)
    logger.addHandler(main_handler)

    error_path = log_path.parent / "erros.log"
    error_handler = RotatingFileHandler(
        error_path,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    audit_path = log_path.parent / "auditoria.jsonl"
    audit_handler = logging.FileHandler(
        audit_path,
        encoding="utf-8",
    )
    audit_handler.setLevel(logging.INFO)
    audit_handler.addFilter(
        lambda record: hasattr(record, "audit_data")
    )
    audit_handler.setFormatter(
        logging.Formatter("%(audit_json)s")
    )
    logger.addHandler(audit_handler)

    return logger


def audit_event(logger, event: str, **details) -> None:
    data = {
        "event": event,
        "details": details,
    }

    logger.info(
        "AUDITORIA %s",
        event,
        extra={
            "audit_data": data,
            "audit_json": json.dumps(
                data,
                ensure_ascii=False,
                default=str,
            ),
        },
    )
