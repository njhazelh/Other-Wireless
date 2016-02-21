#! /usr/bin/env python3

import random
import math
from collections import defaultdict
import multiprocessing
import signal
import itertools
import time

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

    def pick_points(self, n):
        return random.sample(list(self.field_choices), n)

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

    cover_len = len(soln)
    while len(soln) < cover_len * 2:
        soln.add((random.randint(0, width), random.randint(0, height)))

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
    heuristic_one works by choosing a collection of random points from the
    uncovered selections then choosing an access point that is closest to
    one of these points.
    """
    field = Field2D(width, height, ap_range)
    soln = []
    points = set(points)

    def score(point, field_sample):
        return min(map(lambda p: distance(point, p), field_sample))

    while len(field) != 0:
        if len(points) == 1:
            soln.append(points.pop())
            break
        if len(soln) == 0:
            soln.append(points.pop())
            continue
        field_sample = field.pick_points(min(20, len(field)))
        best = min(points, key=lambda p: score(p, field_sample))
        soln.append(best)
        field.filter_within_range(best, ap_range)
        points.remove(best)
    return soln

def heuristic_two(width, height, ap_range, points):
    """
    This heuristic divides the space into blocks with a width and height of the
    access point range.  It randomly chooses between these blocks and randomly
    chooses a point within the block.  This strategy was indented to acheive
    an even distribution over the space.
    """
    field = Field2D(width, height, ap_range)
    soln = []
    points = list(points)
    grid_x = list(range(width // ap_range + 1))
    grid_y = list(range(height // ap_range + 1))

    while True:
        random.shuffle(grid_x)
        random.shuffle(grid_y)
        for point in itertools.product(grid_x, grid_y):
            x, y = point
            if len(field) == 0:
                # The field is covered
                break
            # Get only the points inside the block
            block = list(filter(
                lambda p:
                    p[0] >= x * ap_range and \
                    p[0] < x * ap_range + ap_range and \
                    p[1] >= y * ap_range and \
                    p[1] < y * ap_range + ap_range,
                points))
            if len(block) == 0:
                # No access points are left in this block
                continue
            ap = random.choice(block)
            soln.append(ap)
            field.filter_within_range(ap, ap_range)
            points.remove(ap)
        else:
            # Can only get here if the for loop terminates without a break
            continue
        break

    return soln


class Test(object):
    __slots__ = ["index"]

    def __init__(self, index):
        self.index = index

    def __call__(self, width, height, ap_range):
        print("test %d" % self.index)

        start = time.time()
        data = generate_data(width, height, ap_range)
        h0_soln = heuristic_zero(width, height, ap_range, data)
        h1_soln = heuristic_one(width, height, ap_range, data)
        h2_soln = heuristic_two(width, height, ap_range, data)
        end = time.time()
        print("test complete: ", end - start)

        return {
            "h0": len(h0_soln),
            "h1": len(h1_soln),
            "h2": len(h2_soln),
        }, len(data)

def test_worker(width, height, ap_range, test_queue, result_queue):
    while True:
        next_test = test_queue.get()
        if next_test is None:
            test_queue.task_done()
            break
        lengths, num_extra = next_test(width, height, ap_range)
        lengths["best"] = lengths[min(lengths, key=lengths.get)]
        result_queue.put((lengths, num_extra))
        test_queue.task_done()

def main():
    width = 200
    height = 200
    ap_range = 20
    simulations = 100

    scores = defaultdict(list)

    job_count = multiprocessing.cpu_count()
    print("Starting %d testing processes" % job_count)
    jobs = []
    test_queue = multiprocessing.JoinableQueue()
    result_queue = multiprocessing.Queue()

    test_start = time.time()
    for i in range(job_count):
        j = multiprocessing.Process(target=test_worker, args=(width, height, ap_range, test_queue, result_queue))
        jobs.append(j)
        j.start()

    for i in range(simulations):
        test_queue.put(Test(i))

    for _ in range(job_count):
        test_queue.put(None)

    test_queue.join()
    test_end = time.time()

    print("Tests completed in ", test_end - test_start)

    while simulations:
        result = result_queue.get()
        scores[result[1]] += [result[0]]
        simulations -= 1

    for num_extra in sorted(scores.keys()):
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
        print("%d %.2f %.2f %.2f %.2f" % (num_extra, h0, h1, h2, best))


if __name__ == "__main__":
    main()
