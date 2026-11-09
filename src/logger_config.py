import logging
from pathlib import Path

def configure_logger(log_path: Path) -> logging.Logger:
    logger = logging.getLogger(f"vigiavia_rpa_{log_path.stem}")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
