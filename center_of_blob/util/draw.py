from __future__ import annotations


import numpy as np


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


def draw_point(
    data: np.ndarray,
    point: tuple[int, int],
    color: tuple[int, int, int] = (255, 255, 255),
    center_size: int = 5,
    border_color: tuple[int, int, int] = (255, 255, 255),
) -> None:
    xx, yy = point
    for k in range(center_size):
        for k2 in range(center_size):
            data[xx + k, yy + k2] = color
            data[xx + k, yy - k2] = color
            data[xx - k, yy + k2] = color
            data[xx - k, yy - k2] = color
            data[xx + k2, yy + k] = color
            data[xx - k2, yy + k] = color
            data[xx + k2, yy - k] = color
            data[xx - k2, yy - k] = color

    border_size = 2 if center_size > 4 else 1
    for k in range(center_size + border_size):
        for k2 in range(center_size + border_size):
            if k < center_size and k2 < center_size:
                continue
            data[xx + k, yy + k2] = border_color
            data[xx + k, yy - k2] = border_color
            data[xx - k, yy + k2] = border_color
            data[xx - k, yy - k2] = border_color
            data[xx + k2, yy + k] = border_color
            data[xx - k2, yy + k] = border_color
            data[xx + k2, yy - k] = border_color
            data[xx - k2, yy - k] = border_color
