import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from .config import DEFAULT_INPUT, OUTPUT_DIR, MVP_INBOX_DIR, LOG_DIR
from .logger_config import configure_logger
from .processor import process_batch

def main() -> int:
    parser = argparse.ArgumentParser(description="VigiaVia RPA - processamento de ocorrências viárias")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Caminho do CSV de entrada")
    args = parser.parse_args()

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    logger = configure_logger(LOG_DIR / f"rpa_{stamp}.log")

    try:
        summary = process_batch(args.input, OUTPUT_DIR, MVP_INBOX_DIR, logger)
    except (FileNotFoundError, ValueError, OSError) as exc:
        logger.exception("FALHA_EXECUCAO tipo=%s", type(exc).__name__)
        print(f"Falha na execução: {exc}", file=sys.stderr)
        return 1

    print("\n=== VIGIAVIA RPA | RESUMO ===")
    print(f"Execução: {summary['execution_id']}")
    for key, value in summary["counts"].items():
        print(f"{key}: {value}")
    print(f"Relatório CSV: {summary['csv_path']}")
    print(f"Arquivo de integração JSON: {summary['json_path']}")
    print("Execução concluída.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
