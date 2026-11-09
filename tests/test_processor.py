import csv
import logging
import tempfile
import unittest
from pathlib import Path
from src.processor import process_batch

class ProcessorTests(unittest.TestCase):
    def test_batch_processes_and_exports(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inp = root / "in.csv"
            rows = [
                ["A1","2026-11-09","-23.560000","-46.650000","alta","Buraco grande"],
                ["A2","2026-11-09","-23.560050","-46.650000","media","Perto do primeiro"],
                ["A3","2026-11-09","-23.570000","-46.660000","baixa","Buraco pequeno"],
                ["A4","2026-11-09","999","-46.660000","alta","Coordenada inválida"]
            ]
            with inp.open("w", newline="", encoding="utf-8") as f:
                w = csv.writer(f); w.writerow(["id","data","latitude","longitude","gravidade","descricao"]); w.writerows(rows)
            log = logging.getLogger("test_processor"); log.addHandler(logging.NullHandler())
            result = process_batch(inp, root/"out", root/"inbox", log, 20)
            self.assertEqual(result["counts"]["total"], 4)
            self.assertEqual(result["counts"]["processados"], 2)
            self.assertEqual(result["counts"]["possiveis_duplicados"], 1)
            self.assertEqual(result["counts"]["invalidos"], 1)
            self.assertTrue(result["csv_path"].exists())
            self.assertTrue(result["json_path"].exists())

if __name__ == "__main__":
    unittest.main()
