class Circle():
    __slots__ = ['x', 'y', 'radius', 'point_here', 'in_reach']

    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.point_here = []
        self.in_reach = []

    def connect(self, circle_table, width, height):
        x_min = max(self.x - self.radius, 0)
        x_max = min(self.x + self.radius + 1, width)
        y_min = max(self.y - self.radius, 0)
        y_max = min(self.y + self.radius + 1, height)
        #print "connecting circle %d %d" % (self.x, self.y)
        for x in xrange(x_min, x_max):
            for y in xrange(y_min, y_max):
                if distance((x,y), (self.x, self.y)) <= self.radius:
                    c = circle_table[x][y]
                    self.in_reach.append(c)
                    c.point_here.append(self)

    def disconnect(self, circles):
        for c in self.in_reach:
            for c2 in c.point_here:
                c2.in_reach.remove(c)
            circles.remove(c)


class TentacleField():
    def __init__(self, width, height, circle_radius):
        print "Starting TentacleField generation"
        self.circles = set()
        self.circle_table = defaultdict(dict)
        for x in xrange(width):
            for y in xrange(height):
                c = Circle(x, y, circle_radius)
                self.circles.add(c)
                self.circle_table[x][y] = c

        circles = set(self.circles)
        running = True

        def tentacle_worker(circles, table):
            while running:
                try:
                    if len(circles) % 1000 == 0:
                        print len(circles)
                    circles.pop().connect(self.circle_table, width, height)
                except KeyError as e:
                    print e
                    return

        num_threads = 16
        threads = []
        for i in xrange(num_threads):
            t = threading.Thread(target=tentacle_worker, args=(circles, self.circle_table))
            threads.append(t)
        for t in threads:
            t.start()
        try:
            for t in threads:
                t.join()
        except KeyboardInterrupt:
            running = False
            raise

        print "finished TentacleField generation"

    def filter_within_range(self, point, pt_range):
        self.circle_table[point.x][point.y].disconnect(self.circles)

    def choose_unfilled_point(self):
        return random.sample(self.circles, 1)[0]

    def __len__(self):
        return len(self.circles)
