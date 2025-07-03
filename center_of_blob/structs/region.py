from __future__ import annotations
import math
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
        self._completed = False

    def add_point(self, point: tuple[int, int]) -> None:
        self.points.append(point)
        if len(self.points) > 2:
            self.polygon = Polygon(self.points)

    def _shortest_distance_squared(self, point: tuple[int, int]) -> float:
        x, y = point
        result = float("inf")
        for x2, y2 in self.points:
            d2 = (x - x2) * (x - x2) + (y - y2) * (y - y2)
            if d2 < result:
                result = d2
        return result

    def has_boundary_point(self, point: tuple[int, int], radius: float = 30) -> bool:
        value = self._shortest_distance_squared(point)
        if value > radius * radius:
            return False
        return True

    def distance_to_boundary_point(self, point: tuple[int, int]) -> float:
        value = self._shortest_distance_squared(point)
        return math.sqrt(value)

    def close(self) -> None:
        # 2 or fewer points do not define a polygon.
        if len(self.points) > 2:
            self.add_point(self.points[0])
            self._completed = True

    def contains(self, point: tuple[int, int]) -> bool:
        if not self._completed:
            raise ValueError(f"Region {self.name} is not completed.")
        if self.polygon is None:
            return False
        return self.polygon.contains(Point(*point))

    def __len__(self) -> int:
        return len(self.points)
