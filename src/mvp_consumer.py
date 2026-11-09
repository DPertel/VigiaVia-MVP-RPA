
import json
import sqlite3
from pathlib import Path

from .config import DB_PATH


def consume_file(
    json_path: Path,
    db_path: Path = DB_PATH,
) -> dict:
    """Consome um JSON de ocorrências e evita inserções duplicadas."""

    json_path = Path(json_path)
    db_path = Path(db_path)

    if not json_path.exists():
        raise FileNotFoundError(
            f"JSON de integração não encontrado: {json_path}"
        )

    with json_path.open("r", encoding="utf-8-sig") as file:
        payload = json.load(file)

    items = payload.get("items")

    if not isinstance(items, list):
        raise ValueError("JSON sem lista válida de items")

    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS occurrences (
                occurrence_id TEXT PRIMARY KEY,
                execution_id TEXT,
                occurred_at TEXT,
                latitude REAL,
                longitude REAL,
                severity TEXT,
                priority TEXT,
                description TEXT,
                source TEXT
            )
        """)

        inserted = 0
        already_registered = 0

        for item in items:
            cursor.execute("""
                INSERT OR IGNORE INTO occurrences (
                    occurrence_id,
                    execution_id,
                    occurred_at,
                    latitude,
                    longitude,
                    severity,
                    priority,
                    description,
                    source
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item["occurrence_id"],
                item["execution_id"],
                item["occurred_at"],
                item["latitude"],
                item["longitude"],
                item["severity"],
                item["priority"],
                item["description"],
                item["source"],
            ))

            if cursor.rowcount == 1:
                inserted += 1
            else:
                already_registered += 1

        connection.commit()

        cursor.execute("SELECT COUNT(*) FROM occurrences")
        database_total = cursor.fetchone()[0]

        return {
            "inserted": inserted,
            "already_registered": already_registered,
            "database_total": database_total,
            "database": str(db_path),
        }

    finally:
        connection.close()


def consume_json(
    json_path: Path,
    db_path: Path = DB_PATH,
) -> dict:
    """Mantém compatibilidade com o monitoramento autônomo."""

    return consume_file(json_path, db_path)
