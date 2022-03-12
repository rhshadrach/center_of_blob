from PyQt5.QtWidgets import QScrollArea, QLabel, QScroller
from PyQt5.QtCore import QEvent
from typing import Literal
from PyQt5 import QtGui
from PyQt5.QtCore import Qt

from center_of_blob import analyze


class ScrollLabel(QScrollArea):
    def __init__(self, parent):
        QScrollArea.__init__(self, parent)

        QScroller.grabGesture(self.viewport(), QScroller.LeftMouseButtonGesture)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)

        self.label = QLabel()
        self.setWidget(self.label)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # No image has been loaded yet
        self._height = None

        self._cache = None

        label = self.label
        label.setAlignment(Qt.AlignCenter)
        label.setScaledContents(True)
        label.setStyleSheet("padding: 0px; margin: 0px")
        label.setWordWrap(True)

    def setText(self, text):
        self.label.setText(text)

    def _maybe_init_height(self, parent):
        if self._height is None:
            self._height = parent.channels[0].shape[0] // 4

    def zoom(self, how: Literal['in', 'out']):
        factor = 2.0 if how == 'in' else 0.5
        if self._height <= 10000 or how == 'out':
            self._height = int(factor * self._height)
        self.update_image()

    def reset_image(self):
        self._height = None
        self.update_image()

    def invalidate_cache(self):
        self._cache = None

    def update_image(self):
        parent = self.parent().parent()
        self._maybe_init_height(parent)


        if self._cache is None:
            self._cache = parent.channels.as_rgb(parent.visible_channels())
        arr = self._cache.copy()

        analyze.highlight_points_dict(arr, parent.centers)
        if parent.origin is not None:
            analyze.highlight_point(arr, parent.origin, color=(255, 255, 0))

        for region in parent.regions:
            analyze.highlight_points(arr, region.points, (255, 69, 0))
            analyze.highlight_line_segments(arr, region.points, (255, 69, 0))

        if parent.current_region is not None:
            analyze.highlight_points(arr, parent.current_region.points, (255, 69, 0))
            analyze.highlight_line_segments(arr, parent.current_region.points, (255, 69, 0))

        height, width, channel = arr.shape
        bytes_per_line = 3 * width
        new_image = QtGui.QImage(arr, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
        new_pixmap = QtGui.QPixmap.fromImage(new_image)

        scaled_pixmap = new_pixmap.scaledToHeight(self._height)
        self.label.setPixmap(scaled_pixmap)
        self.label.show()

    def event(self, event: QEvent):
        return super().event(event)
