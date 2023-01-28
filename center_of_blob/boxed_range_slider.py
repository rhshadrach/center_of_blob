from __future__ import annotations

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QAbstractSpinBox

from center_of_blob.range_slider import RangeSlider


class BoxedRangeSlider(QtWidgets.QWidget):
    def __init__(self, minimum: int, maximum: int):
        super().__init__()
        self.slider = RangeSlider(QtCore.Qt.Horizontal)
        self.slider.setTracking(False)
        self.box_low = QtWidgets.QSpinBox()
        self.box_low.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.box_high = QtWidgets.QSpinBox()
        self.box_high.setButtonSymbols(QAbstractSpinBox.NoButtons)

        # Initial values
        self.slider.setMinimum(minimum)
        self.slider.setMaximum(maximum)
        self.slider.setLow(minimum)
        self.slider.setHigh(maximum)
        self.box_low.setRange(minimum, maximum)
        self.box_high.setRange(minimum, maximum)
        self.box_low.setValue(minimum)
        self.box_high.setValue(maximum)

        # Updates
        self.slider.sliderMoved.connect(self.update_from_slider)
        self.box_low.valueChanged.connect(self.update_slider)
        self.box_high.valueChanged.connect(self.update_slider)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.box_low)
        layout.addWidget(self.box_high)
        layout.addWidget(self.slider)

    @QtCore.pyqtSlot(int)
    def update_slider(self):
        low, high = self.box_low.value(), self.box_high.value()
        self.slider.setLow(low)
        self.slider.setHigh(high)

    @QtCore.pyqtSlot(int)
    def update_from_slider(self):
        self.box_low.setValue(self.slider.low())
        self.box_high.setValue(self.slider.high())

    @QtCore.pyqtSlot(int)
    def setMinimum(self, minval):
        self.slider.setMinimum(minval)

    @QtCore.pyqtSlot(int)
    def setMaximum(self, maxval):
        self.slider.setMaximum(maxval)

    @QtCore.pyqtSlot(int, int)
    def setRange(self, minval, maxval):
        self.slider.setRange(minval, maxval)

    @QtCore.pyqtSlot()
    def low(self):
        return self.slider.low()

    @QtCore.pyqtSlot()
    def high(self):
        return self.slider.high()

    @QtCore.pyqtSlot(int)
    def setLow(self, value):
        self.slider.setLow(value)

    @QtCore.pyqtSlot(int)
    def setHigh(self, value):
        self.slider.setHigh(value)

    def isSliderDown(self) -> bool:
        return self.slider.isSliderDown()

    @property
    def valueChanged(self):
        return self.slider.valueChanged


