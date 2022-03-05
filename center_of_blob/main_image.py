from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPixmap
from typing import Literal


class ScrollLabel(QScrollArea):
    def __init__(self, filename):
        QScrollArea.__init__(self)
        self.filename = filename
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)

        self.label = QLabel()
        self.setWidget(self.label)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        label = self.label
        label.setAlignment(Qt.AlignCenter)
        label.setToolTip(filename)
        self.pixmap = QPixmap(filename)
        self._height = self.pixmap.height() // 4
        self._update_image()
        label.setScaledContents(True)
        label.setStyleSheet("border: 3px solid blue; padding: 0px; margin: 0px")
        label.setWordWrap(True)

    def setText(self, text):
        self.label.setText(text)

    def zoom(self, how: Literal['in', 'out']):
        factor = 2.0 if how == 'in' else 0.5
        if self._height <= 10000:
            self._height = int(factor * self._height)
        self._update_image()

    def _update_image(self, pixmap=None):
        if pixmap is not None:
            self.pixmap = pixmap
        scaled_pixmap = self.pixmap.scaledToHeight(self._height)
        self.label.setPixmap(scaled_pixmap)
        self.label.show()

    def event(self, event: QEvent):
        return super().event(event)
