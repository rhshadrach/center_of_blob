from __future__ import annotations

import itertools as it
from collections.abc import Iterable

import numpy as np

from cellcensus.centers import Centers


def highlight_points(
    data: np.ndarray, points: Iterable[tuple[int, int]], color: tuple[int, int, int]
) -> None:
    for point in points:
        highlight_point(data, point, color)


def highlight_points_dict(
    data: np.ndarray,
    centers: Centers,
    show_centers: list[int],
    center_size: int,
    color: tuple[int, int, int] | None = None,
    border_color: tuple[int, int, int] = (255, 255, 255),
) -> None:
    for (x, y), center in centers.items():
        show = False
        for channel in show_centers:
            if center.color[channel - 1] > 0:
                show = True
                break
        if not show:
            continue
        if color is None:
            c = center.color
        else:
            c = color
        highlight_point(data, (x, y), c, center_size, border_color)


def highlight_line_segments(
    data: np.ndarray, points: Iterable[tuple[int, int]], color: tuple[int, int, int]
) -> None:
    for (x1, y1), (x2, y2) in it.pairwise(points):
        draw_line(data, x1, y1, x2, y2, color)


def draw_line(
    mat: np.ndarray, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]
) -> None:
    if not (
        0 <= x0 < mat.shape[0]
        and 0 <= x1 < mat.shape[0]
        and 0 <= y0 < mat.shape[1]
        and 0 <= y1 < mat.shape[1]
    ):
        raise ValueError("Invalid coordinates.")
    if (x0, y0) == (x1, y1):
        mat[x0, y0] = color
        return
    # Swap axes if Y slope is smaller than X slope
    transpose = abs(x1 - x0) < abs(y1 - y0)
    if transpose:
        # mat = mat.T
        mat = np.transpose(mat, (1, 0, 2))
        x0, y0, x1, y1 = y0, x0, y1, x1

    # Swap line direction to go left-to-right if necessary
    if x0 > x1:
        x0, y0, x1, y1 = x1, y1, x0, y0

    # Write line ends
    mat[x0, y0] = color
    mat[x1, y1] = color

    # Compute intermediate coordinates using line equation
    x = np.arange(x0 + 1, x1)
    y = np.round(((y1 - y0) / (x1 - x0)) * (x - x0) + y0).astype(x.dtype)

    # Write intermediate coordinates
    mat[x, y] = color


def highlight_point(
    data: np.ndarray,
    point: tuple[int, int],
    color: tuple[int, int, int] = (255, 255, 255),
    center_size: int = 5,
    border_color: tuple[int, int, int] = (255, 255, 255),
) -> None:
    border_size = 2 if center_size > 4 else 1
    fill_square(data, point, center_size + border_size - 1, border_color)
    fill_square(data, point, center_size - 1, color)


def fill_square(
    data: np.ndarray,
    point: tuple[int, int],
    radius: int,
    color: tuple[int, int, int],
) -> None:
    """Fill the pixels within ``radius`` of ``point``, clipped to ``data``."""
    xx, yy = point
    # Clip at 0 so negative indices don't wrap around to the opposite edge.
    data[
        max(xx - radius, 0) : xx + radius + 1, max(yy - radius, 0) : yy + radius + 1
    ] = color
