
import json
import tempfile
import unittest
from pathlib import Path

from src.mvp_consumer import consume_file


class ConsumerTests(unittest.TestCase):

    def test_consumes_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            database = base / "consumer.sqlite3"
            json_file = base / "ocorrencias.json"

            payload = {
                "items": [
                    {
                        "occurrence_id": "TEST-001",
                        "execution_id": "EXEC-001",
                        "occurred_at": "2026-11-09T10:00:00",
                        "latitude": -23.5505,
                        "longitude": -46.6333,
                        "severity": "alta",
                        "priority": "alta",
                        "description": "Buraco de teste",
                        "source": "camera"
                    }
                ]
            }

            json_file.write_text(
                json.dumps(payload),
                encoding="utf-8"
            )

            # Primeira execução: deve inserir o registro.
            result1 = consume_file(json_file, database)

            self.assertEqual(result1["inserted"], 1)
            self.assertEqual(result1["already_registered"], 0)
            self.assertEqual(result1["database_total"], 1)

            # Segunda execução: não deve inserir novamente.
            result2 = consume_file(json_file, database)

            self.assertEqual(result2["inserted"], 0)
            self.assertEqual(result2["already_registered"], 1)
            self.assertEqual(result2["database_total"], 1)


if __name__ == "__main__":
    unittest.main()
