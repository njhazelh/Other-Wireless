#! /usr/bin/env python3

import random
import math
import multiprocessing
import itertools
import time
import logging

logging.basicConfig(
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%I:%M:%S'
)
log = logging.getLogger()
log.setLevel(logging.INFO)


class Field2D:
    def __init__(self, width, height, pt_range):
        self.width = width
        self.height = height
        self.field_choices = set(itertools.product(range(width), range(height)))
        self.circle = list(
            itertools.filterfalse(
                lambda p: distance((0, 0), p) > pt_range,
            itertools.product(
                range(-pt_range, pt_range+1),
                range(-pt_range, pt_range+1))))


    def filter_within_range(self, point, pt_range):
        self.field_choices
        x, y = point
        for (cx, cy) in self.circle:
            p = (cx+x, cy+y)
            if p in self.field_choices:
                self.field_choices.remove(p)


    def choose_unfilled_point(self):
        return random.choice(list(self.field_choices))


    def sample_field(self, n):
        return random.sample(list(self.field_choices), n)


    def __len__(self):
        return len(self.field_choices)


def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)


def generate_data(width, height, ap_range):
    field = Field2D(width, height, ap_range)
    soln = []

    log.info("Generating data")
    start = time.time()
    while len(field) != 0:
        point = field.choose_unfilled_point()
        soln.append(point)
        field.filter_within_range(point, ap_range)
    end = time.time()
    log.info("Generated Data in %f", end - start)

    cover_len = len(soln)
    while len(soln) < cover_len * 2:
        soln.append((random.randint(0, width), random.randint(0, height)))

    return soln


def heuristic_zero(width, height, ap_range, points):
    """
    This heuristic work by randomly choosing points until the space is
    covered.
    """
    field = Field2D(width, height, ap_range)
    soln = []
    points = set(points)

    while len(field) != 0:
        ap = random.sample(points, 1)[0]
        soln.append(ap)
        field.filter_within_range(ap, ap_range)
        points.remove(ap)

    return soln


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
        field_sample = field.sample_field(min(20, len(field)))
        best = min(points, key=lambda p: score(p, field_sample))
        soln.append(best)
        field.filter_within_range(best, ap_range)
        points.remove(best)
    return soln

def heuristic_two(width, height, ap_range, points):
    """
    This heuristic divides the space into blocks with a width and height of the
    access point range.  It randomly chooses between these blocks and randomly
    chooses a point within the block.  This strategy was intended to acheive
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
        log.info("test %d", self.index)

        start = time.time()
        data = generate_data(width, height, ap_range)
        h0_soln = heuristic_zero(width, height, ap_range, data)
        h1_soln = heuristic_one(width, height, ap_range, data)
        h2_soln = heuristic_two(width, height, ap_range, data)
        end = time.time()
        log.info("test %d complete: %f", self.index, end - start)

        return {
            "h0": len(h0_soln) / len(data),
            "h1": len(h1_soln) / len(data),
            "h2": len(h2_soln) / len(data),
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

    job_count = multiprocessing.cpu_count()
    log.info("Starting %d testing processes", job_count)
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

    log.info("Tests completed in %f", test_end - test_start)

    h0 = 0
    h1 = 0
    h2 = 0
    best = 0
    count = 0
    while simulations:
        result = result_queue.get()
        simulations -= 1
        count += 1
        h0 += result[0]["h0"]
        h1 += result[0]["h1"]
        h2 += result[0]["h2"]
        best += result[0]["best"]

    h0 /= count
    h1 /= count
    h2 /= count
    best /= count

    print("H0: %f" % h0)
    print("H1: %f" % h1)
    print("H2: %f" % h2)
    print("BEST: %f" % best)


if __name__ == "__main__":
    main()
