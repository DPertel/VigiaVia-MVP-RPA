import unittest
from src.deduplication import haversine_meters, find_possible_duplicate

class DeduplicationTests(unittest.TestCase):
    def test_same_point_zero_distance(self):
        self.assertAlmostEqual(haversine_meters(-23.5, -46.6, -23.5, -46.6), 0)
    def test_close_point_detected(self):
        a = {"id":"A1","latitude":-23.5,"longitude":-46.6}
        b = {"id":"A2","latitude":-23.50005,"longitude":-46.6}
        self.assertEqual(find_possible_duplicate(b, [a], 20), "A1")
    def test_far_point_not_detected(self):
        a = {"id":"A1","latitude":-23.5,"longitude":-46.6}
        b = {"id":"A2","latitude":-23.51,"longitude":-46.6}
        self.assertIsNone(find_possible_duplicate(b, [a], 20))

if __name__ == "__main__":
    unittest.main()
