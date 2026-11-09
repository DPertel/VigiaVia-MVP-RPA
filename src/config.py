from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "input" / "ocorrencias.csv"
OUTPUT_DIR = ROOT / "data" / "output"
MVP_INBOX_DIR = ROOT / "data" / "mvp_inbox"
LOG_DIR = ROOT / "logs"
DUPLICATE_RADIUS_METERS = 20.0  # parâmetro de demonstração, não regra oficial do MVP
REQUIRED_COLUMNS = {"id", "data", "latitude", "longitude", "gravidade", "descricao"}
