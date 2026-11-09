import unittest
from src.validator import validate_record

BASE = {"id":"A1","data":"2026-11-09","latitude":"-23.56","longitude":"-46.65",
        "gravidade":"alta","descricao":"Buraco na faixa da direita"}

class ValidatorTests(unittest.TestCase):
    def test_valid_record(self):
        self.assertEqual(validate_record(BASE), (True, ""))
    def test_missing_field(self):
        row = dict(BASE); row["latitude"] = ""
        self.assertFalse(validate_record(row)[0])
    def test_invalid_latitude(self):
        row = dict(BASE); row["latitude"] = "120"
        self.assertIn("Latitude", validate_record(row)[1])
    def test_invalid_date(self):
        row = dict(BASE); row["data"] = "09/11/2026"
        self.assertFalse(validate_record(row)[0])
    def test_invalid_severity(self):
        row = dict(BASE); row["gravidade"] = "urgente"
        self.assertFalse(validate_record(row)[0])

if __name__ == "__main__":
    unittest.main()
