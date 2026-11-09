
import argparse
import logging
import shutil
import signal
import time
from datetime import datetime
from pathlib import Path

from .config import (
    DEFAULT_INPUT,
    OUTPUT_DIR,
    MVP_INBOX_DIR,
    LOG_DIR,
    PENDING_DIR,
    PROCESSED_DIR,
    ERROR_DIR,
    DB_PATH,
    POLL_INTERVAL_SECONDS,
    FILE_STABILITY_SECONDS,
)
from .logger_config import configure_logger, audit_event
from .processor import process_batch
from .mvp_consumer import consume_json


running = True


def request_stop(signum=None, frame=None):
    global running
    running = False


def notify_gui(event_callback, event, message, **details):
    """Envia eventos à interface, adaptando os nomes dos campos."""
    if event_callback is None:
        return

    # Compatibilidade entre os nomes usados pelo processor e pela GUI.
    if "indice" in details and "index" not in details:
        details["index"] = details["indice"]

    if "arquivo" in details and "filename" not in details:
        details["filename"] = details["arquivo"]

    try:
        event_callback(event, message, **details)
    except Exception:
        pass


def move_file(source: Path, destination_dir: Path) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)

    destination = destination_dir / source.name

    if destination.exists():
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination = destination_dir / (
            f"{source.stem}_{stamp}{source.suffix}"
        )

    return Path(shutil.move(str(source), str(destination)))


def wait_until_stable(path: Path) -> bool:
    if not path.exists():
        return False

    first_size = path.stat().st_size
    time.sleep(FILE_STABILITY_SECONDS)

    if not path.exists():
        return False

    second_size = path.stat().st_size

    return first_size == second_size


def print_summary(summary: dict, consumer_result: dict):
    print("\n=== VIGIAVIA RPA | RESUMO ===")
    print(f"Execução: {summary['execution_id']}")

    for key, value in summary["counts"].items():
        print(f"{key}: {value}")

    print(f"Relatório CSV: {summary['csv_path']}")
    print(f"Arquivo JSON: {summary['json_path']}")

    print("\n=== INTEGRAÇÃO SQLITE ===")
    print(f"Novos registros: {consumer_result['inserted']}")
    print(
        "Já cadastrados: "
        f"{consumer_result['already_registered']}"
    )
    print(f"Total no banco: {consumer_result['database_total']}")


def process_file(
    path: Path,
    logger: logging.Logger,
    event_callback=None,
) -> bool:
    print(f"\n[ARQUIVO DETECTADO] {path.name}")

    logger.info("ARQUIVO_DETECTADO nome=%s", path.name)

    notify_gui(
        event_callback,
        "ARQUIVO_DETECTADO",
        f"Arquivo detectado: {path.name}",
        filename=path.name,
    )

    try:
        if not wait_until_stable(path):
            logger.warning(
                "ARQUIVO_AINDA_EM_GRAVACAO nome=%s",
                path.name,
            )
            return False

        notify_gui(
            event_callback,
            "ARQUIVO_RECEBIDO",
            f"Arquivo recebido e pronto para análise: {path.name}",
            filename=path.name,
        )

        notify_gui(
            event_callback,
            "ANALISE_INICIADA",
            f"Iniciando análise de {path.name}.",
            filename=path.name,
        )

        summary = process_batch(
            path,
            OUTPUT_DIR,
            MVP_INBOX_DIR,
            logger,
            include_history=True,
            db_path=DB_PATH,
            event_callback=(
                lambda event, message, **details:
                notify_gui(
                    event_callback,
                    event,
                    message,
                    **details,
                )
            ) if event_callback else None,
        )

        notify_gui(
            event_callback,
            "INTEGRACAO_INICIADA",
            "Enviando ocorrências processadas para o SQLite.",
        )

        consumer_result = consume_json(
            summary["json_path"],
            DB_PATH,
        )

        notify_gui(
            event_callback,
            "SQLITE_CONCLUIDO",
            "Integração com SQLite concluída.",
            inserted=consumer_result["inserted"],
            already_registered=consumer_result["already_registered"],
            database_total=consumer_result["database_total"],
        )

        print_summary(summary, consumer_result)

        archived = move_file(path, PROCESSED_DIR)

        logger.info(
            "ARQUIVO_CONCLUIDO nome=%s destino=%s",
            path.name,
            archived,
        )

        audit_event(
            logger,
            "ARQUIVO_ARQUIVADO",
            arquivo=path.name,
            destino=str(archived),
            execucao=summary["execution_id"],
        )

        notify_gui(
            event_callback,
            "ARQUIVO_ARQUIVADO",
            f"Arquivo arquivado com sucesso: {archived}",
            filename=path.name,
            destino=str(archived),
        )

        print(f"\n[CONCLUÍDO] Arquivo movido para: {archived}")
        return True

    except Exception as exc:
        logger.exception(
            "FALHA_NO_ARQUIVO nome=%s tipo=%s",
            path.name,
            type(exc).__name__,
        )

        audit_event(
            logger,
            "FALHA_NO_ARQUIVO",
            arquivo=path.name,
            tipo=type(exc).__name__,
            mensagem=str(exc),
        )

        notify_gui(
            event_callback,
            "FALHA_NO_ARQUIVO",
            f"Falha ao processar {path.name}: {exc}",
            filename=path.name,
            erro=str(exc),
        )

        try:
            if path.exists():
                moved = move_file(path, ERROR_DIR)
                print(f"[ERRO] Arquivo movido para: {moved}")
        except OSError:
            logger.exception(
                "NAO_FOI_POSSIVEL_MOVER_ARQUIVO nome=%s",
                path.name,
            )

        print(f"[ERRO] Falha ao processar {path.name}: {exc}")
        return False


def run_once(input_path: Path, logger: logging.Logger) -> int:
    if not input_path.exists():
        logger.error("ENTRADA_NAO_ENCONTRADA caminho=%s", input_path)
        print(f"Arquivo não encontrado: {input_path}")
        return 1

    return 0 if process_file(input_path, logger) else 1


def monitor_pending(
    logger: logging.Logger,
    event_callback=None,
):
    global running

    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    ERROR_DIR.mkdir(parents=True, exist_ok=True)

    print("\n=== VIGIAVIA RPA | MONITORAMENTO ===")
    print("Status: ATIVO")
    print(f"Pasta monitorada: {PENDING_DIR}")
    print(f"Intervalo: {POLL_INTERVAL_SECONDS} segundos")
    print("Pressione Ctrl+C para encerrar.")
    print("\nAguardando novos relatos...")

    logger.info(
        "MONITORAMENTO_INICIADO pasta=%s intervalo=%s",
        PENDING_DIR,
        POLL_INTERVAL_SECONDS,
    )

    audit_event(
        logger,
        "MONITORAMENTO_INICIADO",
        pasta=str(PENDING_DIR),
        intervalo_segundos=POLL_INTERVAL_SECONDS,
    )

    notify_gui(
        event_callback,
        "MONITORAMENTO_INICIADO",
        "Monitoramento do VigiaVia iniciado.",
        pasta=str(PENDING_DIR),
    )

    was_waiting = False

    while running:
        try:
            pending_files = sorted(PENDING_DIR.glob("*.csv"))

            if not pending_files:
                if not was_waiting:
                    notify_gui(
                        event_callback,
                        "AGUARDANDO_ARQUIVOS",
                        "Aguardando novos arquivos CSV na pasta de entrada.",
                    )
                    was_waiting = True
            else:
                was_waiting = False

                for path in pending_files:
                    if not running:
                        break

                    if path.exists():
                        process_file(path, logger, event_callback)

            time.sleep(POLL_INTERVAL_SECONDS)

        except Exception:
            logger.exception("ERRO_NO_CICLO_DE_MONITORAMENTO")
            time.sleep(POLL_INTERVAL_SECONDS)

    logger.info("MONITORAMENTO_ENCERRADO")
    audit_event(logger, "MONITORAMENTO_ENCERRADO")

    notify_gui(
        event_callback,
        "MONITORAMENTO_ENCERRADO",
        "Monitoramento encerrado.",
    )

    print("\nMonitoramento encerrado.")


def main() -> int:
    global running

    parser = argparse.ArgumentParser(
        description="VigiaVia RPA - automação de triagem de ocorrências"
    )

    parser.add_argument(
        "--once",
        action="store_true",
        help="Processa um único arquivo e encerra",
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="CSV usado no modo --once",
    )

    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Executa o monitoramento somente pelo terminal",
    )

    args = parser.parse_args()

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = configure_logger(LOG_DIR / "rpa.log")

    signal.signal(signal.SIGINT, request_stop)

    running = True

    if args.once:
        return run_once(args.input, logger)

    if args.input != DEFAULT_INPUT:
        return run_once(args.input, logger)

    if args.no_gui:
        print("Executando VigiaVia sem interface gráfica.")
        monitor_pending(logger)
        return 0

    try:
        from .gui import run_gui

        print("Iniciando interface gráfica do VigiaVia...")
        run_gui(logger, monitor_pending, request_stop)

    except Exception:
        logger.exception(
            "FALHA_AO_INICIAR_INTERFACE_GRAFICA"
        )
        print(
            "\nNão foi possível iniciar a interface gráfica. "
            "O monitoramento continuará pelo terminal."
        )
        running = True
        monitor_pending(logger)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
