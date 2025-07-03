from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from center_of_blob import util


class Centers(dict):
    def closest(
        self, point: tuple[int, int], radius: float | None = None
    ) -> tuple[int, int] | None:
        x, y = point
        closest, shortest_distance = None, None
        for x2, y2 in self:
            distance = (x - x2) * (x - x2) + (y - y2) * (y - y2)
            if closest is None or distance < shortest_distance:
                closest = x2, y2
                shortest_distance = distance

        if shortest_distance is None or (
            radius is not None and shortest_distance > radius * radius
        ):
            return None
        return closest

    def are_in_img(self, shape: tuple[int, int]) -> bool:
        return all(0 <= x < shape[0] and 0 <= y < shape[1] for x, y in self)

    def draw(
        self,
        arr: np.ndarray,
        size: int,
        channels: list[int],
        color_override: tuple[int, int, int] | None = None,
        border_color: tuple[int, int, int] = (255, 255, 255),
    ) -> None:
        for (x, y), center in self.items():
            show = False
            for channel in channels:
                if center.color[channel - 1] > 0:
                    show = True
                    break
            if not show:
                continue
            if color_override is None:
                c = center.color
            else:
                c = color_override
            util.draw_point(arr, (x, y), c, size, border_color)


@dataclass
class Center:
    x: int
    y: int
    color: tuple[int, int, int]
    region: str
