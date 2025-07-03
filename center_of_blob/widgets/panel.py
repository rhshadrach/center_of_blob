from __future__ import annotations
from typing import TYPE_CHECKING, cast
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QApplication, QLabel, QScrollArea, QScroller, QWidget

from center_of_blob import util
import numpy as np

if TYPE_CHECKING:
    from center_of_blob.main import MainWindow


class Panel(QScrollArea):
    def __init__(self, parent: QWidget | None) -> None:
        QScrollArea.__init__(self, parent)

        QScroller.grabGesture(self.viewport(), QScroller.LeftMouseButtonGesture)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)

        self.label = QLabel()
        self.setWidget(self.label)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # No image has been loaded yet.
        self._height: int | None = None
        self._orig_height: int | None = None
        self._height_factor = 1.0

        self._cache: np.ndarray | None = None

        label = self.label
        # label.setAlignment(Qt.AlignCenter)
        label.setScaledContents(True)
        label.setStyleSheet("padding: 0px; margin: 0px")
        label.setWordWrap(True)

        self.installEventFilter(self)

    @property
    def _main_window(self) -> MainWindow:
        return cast("MainWindow", self.parent().parent())

    def setText(self, text: str) -> None:
        self.label.setText(text)

    def _maybe_init_height(self) -> None:
        if self._height is None:
            self._height = self._main_window.channels[0].shape[0] // 4
            self._orig_height = self._height

    def zoom(self, factor: float) -> None:
        assert self._orig_height is not None
        self._height = int(factor * self._orig_height)
        self.update_image()

        halfwidth = self.width() // 2
        halfheight = self.height() // 2

        horz = self.horizontalScrollBar()
        horz.setValue(
            int((horz.value() + halfwidth) * factor / self._height_factor - halfwidth)
        )

        vert = self.verticalScrollBar()
        vert.setValue(
            int((vert.value() + halfheight) * factor / self._height_factor - halfheight)
        )

        self._height_factor = factor

    def reset_image(self) -> None:
        self._height = None
        self.update_image()

    def invalidate_cache(self) -> None:
        self._cache = None

    def update_image(self) -> None:
        main_window = self._main_window
        self._maybe_init_height()

        if self._cache is None:
            channels = main_window.visible_channels()
            if channels is None:
                return
            self._cache = main_window.channels.as_rgb(channels)
        assert self._cache is not None
        arr = self._cache.copy()

        if len(main_window.show_centers) > 0:
            main_window.centers.draw(
                arr=arr,
                size=main_window.center_size_slider.value(),
                channels=main_window.show_centers,
                color_override=None
                if main_window.center_colors == "normal"
                else (0, 0, 0),
                border_color=(
                    (255, 255, 255)
                    if main_window.center_colors == "normal"
                    else (0, 0, 0)
                ),
            )
        if main_window.origin is not None:
            util.draw_point(arr, main_window.origin, color=(255, 255, 0))

        for region in main_window.regions:
            region.draw(arr)
        if main_window.current_region is not None:
            main_window.current_region.draw(arr)

        height, width, channel = arr.shape
        bytes_per_line = 3 * width
        new_image = QtGui.QImage(  # type: ignore[call-overload]
            arr, width, height, bytes_per_line, QtGui.QImage.Format_RGB888
        )
        new_pixmap = QtGui.QPixmap.fromImage(new_image)

        assert self._height is not None
        scaled_pixmap = new_pixmap.scaledToHeight(self._height)
        self.label.setScaledContents(False)
        self.label.setPixmap(scaled_pixmap)
        # self.label.setAlignment(Qt.AlignCenter)
        self.label.show()

    def event(self, event: QEvent) -> bool:
        return super().event(event)

    def eventFilter(self, source: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if event.type() == QtCore.QEvent.Wheel:
            modifiers = QApplication.keyboardModifiers()
            if bool(modifiers == QtCore.Qt.ControlModifier):
                return True
        return super().eventFilter(source, event)
