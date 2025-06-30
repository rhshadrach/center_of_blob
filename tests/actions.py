import contextlib
import functools as ft
from typing import Generator

import pytest
import pytestqt.qtbot
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QInputDialog, QMessageBox

from center_of_blob.main import MainWindow
from center_of_blob import popups
from tests import data


def setup_test(qtbot: pytestqt.qtbot.QtBot) -> MainWindow:
    main = MainWindow()
    # Always use the same Window size for pixel consistency
    main.showNormal()
    main.setGeometry(100, 100, 1000, 1000)
    main.hide()
    qtbot.addWidget(main)
    return main


def load_image(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    main: MainWindow,
    filename: str,
) -> None:
    path = data.resolve_path(filename)
    monkeypatch.setattr(popups, "get_image_filename", lambda *args, **kwargs: path)
    qtbot.mouseClick(main.img_path_button, QtCore.Qt.LeftButton)


def load_csv(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    main: MainWindow,
    filename: str,
) -> None:
    path = data.resolve_path(filename)
    monkeypatch.setattr(popups, "get_centers_filename", lambda *args, **kwargs: path)
    qtbot.mouseClick(main.centers_path_button, QtCore.Qt.LeftButton)


def save_csv(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    main: MainWindow,
    filename: str,
) -> None:
    monkeypatch.setattr(
        popups, "get_csv_save_filename", lambda *args, **kwargs: filename
    )
    qtbot.mouseClick(main.write_csv_button, QtCore.Qt.LeftButton)


def click_color_channel(
    qtbot: pytestqt.qtbot.QtBot, main: MainWindow, channel: int
) -> None:
    qtbot.mouseClick(main.mouse_colors[channel - 1], QtCore.Qt.LeftButton)


def click_modify_centers(qtbot: pytestqt.qtbot.QtBot, main: MainWindow) -> None:
    qtbot.mouseClick(main.modify_centers, QtCore.Qt.LeftButton)


def click_draw_region(qtbot: pytestqt.qtbot.QtBot, main: MainWindow) -> None:
    qtbot.mouseClick(main.draw_region, QtCore.Qt.LeftButton)


def click_set_origin(qtbot: pytestqt.qtbot.QtBot, main: MainWindow) -> None:
    qtbot.mouseClick(main.set_origin_button, QtCore.Qt.LeftButton)


def click_main_image(
    qtbot: pytestqt.qtbot.QtBot, main: MainWindow, points: list[tuple[int, int]]
) -> None:
    for point in points:
        pos = QtCore.QPoint(*point)
        qtbot.mouseClick(main.label.label, QtCore.Qt.LeftButton, pos=pos)


@contextlib.contextmanager
def setup_close_message_box(qtbot: pytestqt.qtbot.QtBot) -> Generator[None, None, None]:
    QtCore.QTimer.singleShot(500, ft.partial(close_message_box, qtbot))
    try:
        yield
    finally:
        pass


@contextlib.contextmanager
def setup_close_region_name_box(
    qtbot: pytestqt.qtbot.QtBot, text_value: str
) -> Generator[None, None, None]:
    QtCore.QTimer.singleShot(500, ft.partial(write_region_name, qtbot, text_value))
    try:
        yield
    finally:
        pass


def write_region_name(qtbot: pytestqt.qtbot.QtBot, text_value: str) -> None:
    window = QApplication.activeWindow()
    if isinstance(window, QInputDialog):
        window.setTextValue(text_value)
        window.accept()


def close_message_box(qtbot: pytestqt.qtbot.QtBot) -> None:
    window = QApplication.activeWindow()
    if isinstance(window, QMessageBox):
        close_button = window.button(QMessageBox.Ok)
        qtbot.mouseClick(close_button, QtCore.Qt.LeftButton)


def window_accept() -> None:
    window = QApplication.activeWindow()
    if isinstance(window, QMessageBox):
        window.accept()
