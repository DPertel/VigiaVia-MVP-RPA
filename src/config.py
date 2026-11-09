
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
PENDING_DIR = INPUT_DIR / "pendentes"
PROCESSED_DIR = DATA_DIR / "processados"
ERROR_DIR = DATA_DIR / "erros"

DEFAULT_INPUT = INPUT_DIR / "ocorrencias.csv"
OUTPUT_DIR = DATA_DIR / "output"
MVP_INBOX_DIR = DATA_DIR / "mvp_inbox"
DB_PATH = DATA_DIR / "mvp_consumer.sqlite3"

LOG_DIR = ROOT / "logs"
MAIN_LOG = LOG_DIR / "rpa.log"
ERROR_LOG = LOG_DIR / "erros.log"
AUDIT_LOG = LOG_DIR / "auditoria.jsonl"

DUPLICATE_RADIUS_METERS = 20.0
POLL_INTERVAL_SECONDS = 3
FILE_STABILITY_SECONDS = 1

REQUIRED_COLUMNS = {
    "id",
    "data",
    "latitude",
    "longitude",
    "gravidade",
    "descricao",
}
