from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from center_of_blob import util


@dataclass
class Center:
    x: int
    y: int
    color: tuple[int, int, int]
    region: str


class Centers(list):
    def _closest_idx(
        self, point: tuple[int, int], radius: float | None = None
    ) -> int | None:
        x, y = point
        closest_idx, shortest_distance = None, None
        for idx, center in enumerate(self):
            x2, y2 = center.x, center.y
            distance = (x - x2) * (x - x2) + (y - y2) * (y - y2)
            if closest_idx is None or distance < shortest_distance:
                closest_idx = idx
                shortest_distance = distance

        if shortest_distance is None or (
            radius is not None and shortest_distance > radius * radius
        ):
            return None
        return closest_idx

    def closest(
        self, point: tuple[int, int], radius: float | None = None
    ) -> Center | None:
        idx = self._closest_idx(point=point, radius=radius)
        result = None if idx is None else self[idx]
        return result

    def remove_closest(
        self, point: tuple[int, int], radius: float | None = None
    ) -> bool:
        idx = self._closest_idx(point=point, radius=radius)
        if idx is not None:
            del self[idx]
        return idx is not None

    def are_in_img(self, shape: tuple[int, int]) -> bool:
        return all(
            0 <= center.x < shape[0] and 0 <= center.y < shape[1] for center in self
        )

    def draw(
        self,
        arr: np.ndarray,
        size: int,
        channels: list[int],
        color_override: tuple[int, int, int] | None = None,
        border_color: tuple[int, int, int] = (255, 255, 255),
    ) -> None:
        for center in self:
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
            util.draw_point(arr, (center.x, center.y), c, size, border_color)
