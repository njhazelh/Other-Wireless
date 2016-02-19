import unittest
import itertools
from network_planning import *

class NetworkPlanningTests(unittest.TestCase):

    def test_avg_distance(self):
        self.assertEqual(avg_dist(3, [1,2,5], lambda x, y: x - y), 1.0/3)

    def test_generate_date(self):
        for i in xrange(50, 160):
            data = generate_data(200, 200, i)
            for p in itertools.permutations(range(200), 2):
                if not any((distance(p0, p) <= i for p0 in data)):
                    self.fail()

        points = [(x, y) for x in xrange(10) for y in xrange(10)]
        data = generate_data(10, 10, 1)
        for p in itertools.permutations(range(10), 2):
            if not any((distance(p0, p) <= 1 for p0 in data)):
                self.fail()
