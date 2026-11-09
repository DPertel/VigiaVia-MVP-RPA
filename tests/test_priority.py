import unittest
from src.priority import classify_priority

class PriorityTests(unittest.TestCase):
    def test_priority_rules(self):
        self.assertEqual(classify_priority("alta"), "ALTA")
        self.assertEqual(classify_priority("media"), "MEDIA")
        self.assertEqual(classify_priority("baixa"), "BAIXA")
    def test_unknown_severity(self):
        with self.assertRaises(ValueError):
            classify_priority("critica")

if __name__ == "__main__":
    unittest.main()
