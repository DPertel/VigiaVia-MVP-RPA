
"""Componente local demonstrativo que consome o JSON exportado pelo RPA.

Representa um segundo componente CitizenTech por meio de uma base SQLite local.
Não se conecta à API de produção do VigiaVia.
"""

import argparse
import json
import sqlite3
from pathlib import Path

from .config import ROOT


DB_PATH = ROOT / "data" / "mvp_consumer.sqlite3"


def consume_file(json_path: Path, db_path: Path = DB_PATH) -> dict:
    """Consome o JSON gerado pelo RPA e registra as ocorrências no SQLite."""

    # Verifica se o arquivo JSON existe.
    if not json_path.exists():
        raise FileNotFoundError(
            f"Arquivo JSON não encontrado: {json_path}"
        )

    # Carrega e valida a estrutura principal do JSON.
    payload = json.loads(json_path.read_text(encoding="utf-8"))

    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        raise ValueError(
            "Contrato inválido: esperado objeto JSON com lista 'items'"
        )

    # Garante que a pasta do banco de dados exista.
    db_path.parent.mkdir(parents=True, exist_ok=True)

    inserted = 0
    duplicates = 0

    # Abre a conexão com o banco de dados.
    conn = sqlite3.connect(db_path)

    try:
        # Garante a execução da transação.
        with conn:

            # Cria a tabela caso ela ainda não exista.
            conn.execute("""
                CREATE TABLE IF NOT EXISTS occurrences (
                    occurrence_id TEXT PRIMARY KEY,
                    execution_id TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    severity TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    description TEXT NOT NULL,
                    source TEXT NOT NULL
                )
            """)

            # Percorre todas as ocorrências recebidas no JSON.
            for item in payload["items"]:

                required = (
                    "occurrence_id",
                    "execution_id",
                    "occurred_at",
                    "latitude",
                    "longitude",
                    "severity",
                    "priority",
                    "description",
                    "source"
                )

                # Valida os campos obrigatórios.
                if not isinstance(item, dict) or any(
                    key not in item for key in required
                ):
                    raise ValueError(
                        "Item do JSON não atende ao contrato de integração"
                    )

                # Insere a ocorrência somente se ela ainda não existir.
                cur = conn.execute("""
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
                    float(item["latitude"]),
                    float(item["longitude"]),
                    item["severity"],
                    item["priority"],
                    item["description"],
                    item["source"]
                ))

                # Identifica se o registro foi inserido ou já existia.
                if cur.rowcount:
                    inserted += 1
                else:
                    duplicates += 1

            # Consulta a quantidade total de registros armazenados.
            total = conn.execute(
                "SELECT COUNT(*) FROM occurrences"
            ).fetchone()[0]

    finally:
        # Fecha a conexão somente após concluir todas as operações.
        conn.close()

    # Retorna o resumo do processamento.
    return {
        "inserted": inserted,
        "already_registered": duplicates,
        "database_total": total,
        "database": str(db_path)
    }


def main() -> int:
    """Executa o consumidor pela linha de comando."""

    parser = argparse.ArgumentParser(
        description="Consumidor local demonstrativo do VigiaVia MVP"
    )

    parser.add_argument(
        "json_file",
        type=Path,
        help="JSON gerado pelo RPA"
    )

    args = parser.parse_args()

    try:
        result = consume_file(args.json_file)

    except (
        FileNotFoundError,
        ValueError,
        OSError,
        json.JSONDecodeError,
        sqlite3.Error
    ) as exc:
        print(f"Falha no consumo: {exc}")
        return 1

    print("=== COMPONENTE CONSUMIDOR CITIZENTECH ===")
    print(f"Novos registros: {result['inserted']}")
    print(
        f"Já existentes (idempotência): "
        f"{result['already_registered']}"
    )
    print(f"Total no banco local: {result['database_total']}")
    print(f"Banco SQLite: {result['database']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
