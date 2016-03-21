import unittest
import itertools
from network_planning import *

class NetworkPlanningTests(unittest.TestCase):

    def test_avg_distance(self):
        self.assertEqual(avg_dist(3, [1, 2, 5], lambda x, y: x - y), 1.0 / 3)

    def test_generate_date(self):
        for i in range(10):
            data = generate_data(100, 100, 20)
            for p in itertools.product(range(100), range(100)):
                if not any((distance(p0, p) <= 20 for p0 in data)):
                    self.fail(p)

        points = [(x, y) for x in range(10) for y in range(10)]
        data = generate_data(10, 10, 1)
        for p in itertools.product(range(10), range(10)):
            if not any((distance(p0, p) <= 1 for p0 in data)):
                self.fail()
