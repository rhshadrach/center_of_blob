import contextlib
import functools as ft

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QInputDialog, QMessageBox

from center_of_blob.main import MainWindow
from center_of_blob.popups import CentersFileDialog, CsvNameDialog, ImageNameDialog
from tests import data


def setup_test(qtbot):
    main = MainWindow()
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


def click_draw_region(qtbot, main):
    qtbot.mouseClick(main.draw_region, QtCore.Qt.LeftButton)


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


@contextlib.contextmanager
def setup_close_region_name_box(qtbot, text_value):
    QtCore.QTimer.singleShot(500, ft.partial(write_region_name, qtbot, text_value))
    try:
        yield
    finally:
        pass


def write_region_name(qtbot, text_value):
    window = QApplication.activeWindow()
    if isinstance(window, QInputDialog):
        window.setTextValue(text_value)
        window.accept()


def close_message_box(qtbot):
    window = QApplication.activeWindow()
    if isinstance(window, QMessageBox):
        close_button = window.button(QMessageBox.Ok)
        qtbot.mouseClick(close_button, QtCore.Qt.LeftButton)


def window_accept():
    window = QApplication.activeWindow()
    if isinstance(window, QMessageBox):
        window.accept()
