from __future__ import annotations

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QApplication, QLabel, QScrollArea, QScroller

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
        self._orig_height = None
        self._height_factor = 1.0

        self._cache = None

        label = self.label
        label.setAlignment(Qt.AlignCenter)
        label.setScaledContents(True)
        label.setStyleSheet("padding: 0px; margin: 0px")
        label.setWordWrap(True)

        self.installEventFilter(self)

    def setText(self, text):
        self.label.setText(text)

    def _maybe_init_height(self, parent):
        if self._height is None:
            self._height = parent.channels[0].shape[0] // 4
            self._orig_height = self._height

    def zoom(self, factor: float):
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

        if len(parent.show_centers) > 0:
            center_size = parent.center_size_slider.value()
            color = None if parent.center_colors == "normal" else (0, 0, 0)
            border_color = (
                (255, 255, 255) if parent.center_colors == "normal" else (0, 0, 0)
            )
            analyze.highlight_points_dict(
                arr,
                parent.centers,
                parent.show_centers,
                center_size,
                color,
                border_color,
            )
        if parent.origin is not None:
            analyze.highlight_point(arr, parent.origin, color=(255, 255, 0))

        for region in parent.regions:
            analyze.highlight_points(arr, region.points, (240, 50, 230))
            analyze.highlight_line_segments(arr, region.points, (240, 50, 230))

        if parent.current_region is not None:
            analyze.highlight_points(arr, parent.current_region.points, (240, 50, 230))
            analyze.highlight_line_segments(
                arr, parent.current_region.points, (240, 50, 230)
            )

        height, width, channel = arr.shape
        bytes_per_line = 3 * width
        new_image = QtGui.QImage(
            arr, width, height, bytes_per_line, QtGui.QImage.Format_RGB888
        )
        new_pixmap = QtGui.QPixmap.fromImage(new_image)

        scaled_pixmap = new_pixmap.scaledToHeight(self._height)
        self.label.setPixmap(scaled_pixmap)
        self.label.show()

    def event(self, event: QEvent):
        return super().event(event)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.Wheel:
            modifiers = QApplication.keyboardModifiers()
            if bool(modifiers == QtCore.Qt.ControlModifier):
                return True
        return super().eventFilter(source, event)
