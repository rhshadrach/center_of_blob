import contextlib
import functools as ft

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMessageBox

from center_of_blob.main import QLabelDemo
from center_of_blob.popups import CentersFileDialog, CsvNameDialog, ImageNameDialog
from tests import data


def setup_test(qtbot):
    main = QLabelDemo()
    # Always use the same Window size for pixel consistency
    main.showNormal()
    main.setGeometry(100, 100, 1000, 1000)
    main.hide()
    qtbot.addWidget(main)
    return main


def load_image(monkeypatch, qtbot, main, filename):
    path = data.resolve_path(filename)
    monkeypatch.setattr(
        ImageNameDialog, "getOpenFileName", lambda *args, **kwargs: path
    )
    qtbot.mouseClick(main.img_path_button, QtCore.Qt.LeftButton)


def load_csv(monkeypatch, qtbot, main, filename):
    path = data.resolve_path(filename)
    monkeypatch.setattr(
        CentersFileDialog, "getOpenFileName", lambda *args, **kwargs: path
    )
    qtbot.mouseClick(main.centers_path_button, QtCore.Qt.LeftButton)


def save_csv(monkeypatch, qtbot, main, filename):
    monkeypatch.setattr(
        CsvNameDialog, "getSaveFileName", lambda *args, **kwargs: filename
    )
    qtbot.mouseClick(main.write_csv_button, QtCore.Qt.LeftButton)


def click_color_channel(qtbot, main, channel):
    qtbot.mouseClick(main.mouse_colors[channel - 1], QtCore.Qt.LeftButton)


def click_modify_centers(qtbot, main):
    qtbot.mouseClick(main.modify_centers, QtCore.Qt.LeftButton)


def click_set_origin(qtbot, main):
    qtbot.mouseClick(main.set_origin_button, QtCore.Qt.LeftButton)


def click_main_image(qtbot, main, points):
    for point in points:
        pos = QtCore.QPoint(*point)
        qtbot.mouseClick(main.label.label, QtCore.Qt.LeftButton, pos=pos)


@contextlib.contextmanager
def setup_close_message_box(qtbot):
    QtCore.QTimer.singleShot(500, ft.partial(close_message_box, qtbot))
    try:
        yield
    finally:
        pass


def close_message_box(qtbot):
    window = QApplication.activeWindow()
    if isinstance(window, QMessageBox):
        close_button = window.button(QMessageBox.Ok)
        qtbot.mouseClick(close_button, QtCore.Qt.LeftButton)
