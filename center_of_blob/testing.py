from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from center_of_blob.main import MainWindow


# TODO: Hardcode somehow instead of using main
def pos_to_pixel(pos: tuple[int, int], main: MainWindow) -> tuple[int, int]:
    x = int(pos[0] / main.label.label.pixmap().width() * main.channels.width)
    y = int(pos[1] / main.label.label.pixmap().height() * main.channels.height)
    return x, y
