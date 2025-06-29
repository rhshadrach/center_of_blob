from __future__ import annotations

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


class Region:
    def __init__(
        self, points: list[tuple[int, int]] | None = None, name: str = "Unnamed"
    ):
        if points is None:
            points = []
        self.points = points
        self.polygon = None
        # TODO: Make protected, type as str | None
        self.name = name

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

    def contains_point(self, point, radius=30):
        x, y = point
        closest, shortest_distance = None, None
        for x2, y2 in self.points:
            distance = (x - x2) * (x - x2) + (y - y2) * (y - y2)
            if closest is None or distance < shortest_distance:
                closest = x2, y2
                shortest_distance = distance

        if shortest_distance is None or (
            radius is not None and shortest_distance > radius * radius
        ):
            return False
        return True

    def __len__(self):
        return len(self.points)
