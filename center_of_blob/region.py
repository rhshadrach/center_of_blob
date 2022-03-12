from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


class Region:
    def __init__(self):
        self.points = []
        self.polygon = None
        self.name = 'Unnamed'

    def add_point(self, point):
        self.points.append(point)
        if len(self.points) > 2:
            self.polygon = Polygon(self.points)

    def close(self):
        if len(self.points) > 0:
            self.add_point(self.points[0])

    def contains(self, point):
        if self.polygon is None:
            return False
        return self.polygon.contains(Point(*point))

    def __len__(self):
        return len(self.points)
