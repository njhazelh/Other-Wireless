#! /usr/bin/env python

import random
import math
from collections import defaultdict
import multiprocessing
import signal
import itertools
import time

AP_RANGE  = 200     # meters
AREA_WIDTH = 2000   # meters
AREA_HEIGHT = 2000  # meters

class Field2D:
    def __init__(self, width, height, pt_range):
        self.width = width
        self.height = height
        #print("starting field init")
        self.field_choices = set(itertools.product(range(width), range(height)))
        self.circle = list(itertools.filterfalse(lambda p: distance((0, 0), p) > pt_range, itertools.product(range(-pt_range, pt_range+1), range(-pt_range, pt_range+1))))
        #print("finished field init", len(self.circle))
        #print (0, 0) in self.circle

    def filter_within_range(self, point, pt_range):
        #print("removing around ", x, y, len(self.field_choices))
        self.field_choices
        x, y = point
        for (cx, cy) in self.circle:
            p = (cx+x, cy+y)
            if p in self.field_choices:
                #print "removing", p
                self.field_choices.remove(p)
        #print("done removing around ", x, y, len(self.field_choices))
        #print (x, y), "in field:", (x, y) in self.field_choices

    def choose_unfilled_point(self):
        choice = random.choice(list(self.field_choices))
        #print choice in self.field_choices
        return choice

    def __len__(self):
        return len(self.field_choices)

def random_points(max_x, max_y, count):
    return {
        (random.randint(0, max_x-1), random.randint(0, max_y-1)) \
        for _ in range(count)}

def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def generate_data(width, height, ap_range):
    field = Field2D(width, height, ap_range)
    soln = set()

    print("Generating data")
    start = time.time()
    while len(field) != 0:
        point = field.choose_unfilled_point()
        soln.add(point)
        field.filter_within_range(point, ap_range)
    end = time.time()
    print("Generated Data:", end - start)

    return soln

def heuristic_zero(width, height, ap_range, points):
    field = Field2D(width, height, ap_range)
    soln = []
    points = set(points)

    while len(field) != 0:
        ap = random.sample(points, 1)[0]
        soln.append(ap)
        field.filter_within_range(ap, ap_range)
        points.remove(ap)

    return soln

def avg_dist(v0, vals, f):
    """
    This function computes the average value of some function f applied
    between v and a series of other values.

    For example: If v were 3, vals was [1, 2, 3], and f was '-'
        then the result of avg_dist would be (3-1 + 3-2 + 3-3) / 3
    """
    return float(sum([f(v0, v) for v in vals])) / len(vals)

def heuristic_one(width, height, ap_range, points):
    """
    heuristic_one works by choosing the point that maximizes the distance to
    the points that a left to choose from.
    """
    field = Field2D(width, height, ap_range)
    soln = []
    points = set(points)

    def score(point):
        pts = list(points)
        pts.remove(point)
        return avg_dist(point, pts, distance)

    while len(field) != 0:
        if len(points) == 1:
            soln.append(points.pop())
            break
        best = max(points, key=score)
        soln.append(best)
        field.filter_within_range(best, ap_range)
        points.remove(best)
    return soln

def heuristic_two(width, height, ap_range, points):
    """
    """
    field = Field2D(width, height, ap_range)
    soln = []
    start_points = list(points)
    start_points += [(0,0),(width,0),(0,height),(width,height)]
    points = list(points)

    def score(point):
        return avg_dist(point, start_points, distance)

    while len(field) != 0:
        if len(points) == 1:
            soln.append(points.pop())
            break
        best = min(points, key=score)
        soln.append(best)
        field.filter_within_range(best, ap_range)
        points.remove(best)
    return soln


class Test(object):
    __slots__ = ["num_extra", "index"]

    def __init__(self, num_extra, index):
        self.num_extra = num_extra
        self.index = index

    def __call__(self, data, width, height, ap_range):
        print("m = %2d: %d" % (self.num_extra, self.index))
        test_data = data.union(random_points(width, height, self.num_extra))

        start = time.time()
        h0_soln = heuristic_zero(width, height, ap_range, test_data)
        h1_soln = heuristic_one(width, height, ap_range, test_data)
        h2_soln = heuristic_two(width, height, ap_range, test_data)
        end = time.time()
        print("test complete: ", end - start)

        return {
            "h0": len(h0_soln),
            "h1": len(h1_soln),
            "h2": len(h2_soln),
        }, self.num_extra

def test_worker(data, width, height, ap_range, test_queue, result_queue):
    while True:
        next_test = test_queue.get()
        if next_test is None:
            test_queue.task_done()
            break
        lengths, num_extra = next_test(data, width, height, ap_range)
        lengths["best"] = lengths[min(lengths, key=lengths.get)]
        result_queue.put((lengths, num_extra))
        test_queue.task_done()

def main():
    width = 2000
    height = 2000
    ap_range = 200
    simulations = 1000
    max_extra = 20
    sim_per_extra = simulations // max_extra

    data = generate_data(width, height, ap_range)

    scores = defaultdict(list)

    job_count = multiprocessing.cpu_count()
    print("Starting %d testing processes" % job_count)
    jobs = []
    test_queue = multiprocessing.JoinableQueue()
    result_queue = multiprocessing.Queue()

    test_start = time.time()
    for i in range(job_count):
        j = multiprocessing.Process(target=test_worker, args=(data, width, height, ap_range, test_queue, result_queue))
        jobs.append(j)
        j.start()

    for num_extra in range(1, max_extra + 1):
        for i in range(sim_per_extra):
            test_queue.put(Test(num_extra, i))

    for _ in range(job_count):
        test_queue.put(None)

    test_queue.join()
    test_end = time.time()

    print("Tests completed in ", test_end - test_start)

    while simulations:
        result = result_queue.get()
        scores[result[1]] += [result[0]]
        simulations -= 1

    for num_extra in scores:
        h0 = 0
        h1 = 0
        h2 = 0
        best = 0
        for result in scores[num_extra]:
            h0 += result["h0"]
            h1 += result["h1"]
            h2 += result["h2"]
            best += result["best"]
        if len(scores[num_extra]) != 0:
            num_results = float(len(scores[num_extra]))
            h0 /= num_results
            h1 /= num_results
            h2 /= num_results
            best /= num_results
        print(h0, h1, h2, best)


if __name__ == "__main__":
    main()
