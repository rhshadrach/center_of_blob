from __future__ import annotations

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


class Region:
    def __init__(
        self, points: list[tuple[int, int]] | None = None, name: str = "Unnamed"
    ) -> None:
        if points is None:
            points = []
        self.points = points
        self.polygon = None
        # TODO: Make protected, type as str | None
        self.name = name

    def add_point(self, point: tuple[int, int]) -> None:
        self.points.append(point)
        if len(self.points) > 2:
            self.polygon = Polygon(self.points)

    def close(self) -> None:
        if len(self.points) > 0:
            self.add_point(self.points[0])

    def contains(self, point: tuple[int, int]) -> bool:
        if self.polygon is None:
            return False
        return self.polygon.contains(Point(*point))

    def contains_point(self, point: tuple[int, int], radius: float = 30) -> bool:
        x, y = point
        shortest_distance: float | None = None
        for x2, y2 in self.points:
            distance = (x - x2) * (x - x2) + (y - y2) * (y - y2)
            if shortest_distance is None or distance < shortest_distance:
                shortest_distance = distance

        if shortest_distance is None or (
            radius is not None and shortest_distance > radius * radius
        ):
            return False
        return True

    def __len__(self) -> int:
        return len(self.points)
