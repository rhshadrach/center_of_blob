from __future__ import annotations


# TODO: Hardcode somehow instead of using main
def pos_to_pixel(pos: tuple[int, int], main) -> tuple[int, int]:
    x = int(pos[0] / main.label.label.width() * main.channels.width)
    y = int(pos[1] / main.label.label.height() * main.channels.height)
    return x, y
