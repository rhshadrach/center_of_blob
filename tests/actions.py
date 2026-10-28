import contextlib
import functools as ft
from collections.abc import Generator

import pytest
import pytestqt.qtbot
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QInputDialog, QMessageBox

import center_of_blob.testing as tm
from center_of_blob import popups
from center_of_blob.main import MainWindow
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


def right_click_main_image(
    qtbot: pytestqt.qtbot.QtBot, main: MainWindow, points: list[tuple[int, int]]
) -> None:
    for point in points:
        pos = QtCore.QPoint(*point)
        qtbot.mouseClick(main.label.label, QtCore.Qt.RightButton, pos=pos)


def pixel_at(main: MainWindow, pos: tuple[int, int]) -> tuple[int, int]:
    """Image pixel (row, column) under the widget position ``pos`` (x, y).

    Unlike ``tm.pos_to_pixel``, this is correct when x != y.
    """
    return tm.pos_to_pixel((pos[1], pos[0]), main)


def answer_region_names(
    monkeypatch: pytest.MonkeyPatch, answers: list[tuple[str, bool]]
) -> list[tuple[str, bool]]:
    """Answer the region name dialog with each (text, accepted) in turn.

    Returns the list of answers still unused, so tests can check the dialog was
    asked exactly as often as expected.
    """
    remaining = list(answers)

    def get_text(*args: object) -> tuple[str, bool]:
        if not remaining:
            raise AssertionError("the region name dialog was asked too often")
        return remaining.pop(0)

    monkeypatch.setattr(QInputDialog, "getText", get_text)
    return remaining


def draw_region(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    main: MainWindow,
    points: list[tuple[int, int]],
    name: str,
) -> None:
    """Draw a region and answer the region name dialog with ``name``."""
    remaining = answer_region_names(monkeypatch, [(name, True)])
    click_draw_region(qtbot, main)
    click_main_image(qtbot, main, points)
    click_draw_region(qtbot, main)
    assert remaining == []


def press_key(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    main: MainWindow,
    key: QtCore.Qt.Key,
    ctrl: bool = False,
) -> None:
    # MainWindow reads the global modifier state rather than the event's.
    modifiers = QtCore.Qt.ControlModifier if ctrl else QtCore.Qt.NoModifier
    monkeypatch.setattr(QApplication, "keyboardModifiers", lambda: modifiers)
    qtbot.keyClick(main, key, modifiers)


def move_mouse(main: MainWindow, point: tuple[int, int]) -> None:
    event = QtGui.QMouseEvent(
        QtCore.QEvent.MouseMove,
        QtCore.QPointF(*point),
        QtCore.Qt.NoButton,
        QtCore.Qt.NoButton,
        QtCore.Qt.NoModifier,
    )
    QApplication.sendEvent(main.label.label, event)


def ctrl_scroll(monkeypatch: pytest.MonkeyPatch, main: MainWindow, delta: int) -> None:
    monkeypatch.setattr(
        QApplication, "keyboardModifiers", lambda: QtCore.Qt.ControlModifier
    )
    event = QtGui.QWheelEvent(
        QtCore.QPointF(5, 5),
        QtCore.QPointF(5, 5),
        QtCore.QPoint(0, 0),
        QtCore.QPoint(0, delta),
        QtCore.Qt.NoButton,
        QtCore.Qt.ControlModifier,
        QtCore.Qt.NoScrollPhase,
        False,
    )
    QApplication.sendEvent(main.label.label, event)


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


def check_invariants(main: MainWindow) -> list[str]:
    """Return the ways in which ``main``'s state is inconsistent.

    These should hold after any sequence of user actions.
    """
    problems = []
    for name, button in main.button_states.items():
        label_text = name.replace("_", " ")
        expected = f"Stop {label_text}" if main.state == name else f"Start {label_text}"
        if button.text() != expected:
            problems.append(f"{name} button reads {button.text()!r} in {main.state!r}")
    if (main.state == "drawing_region") != (main.current_region is not None):
        problems.append(
            f"state is {main.state!r} but current_region is {main.current_region!r}"
        )
    checked = {k: box.isChecked() for k, box in enumerate(main.mouse_colors)}
    if checked != main.colors:
        problems.append(f"color checkboxes {checked} != colors {main.colors}")
    shown = [k for k in range(1, 4) if main.show_center_checkboxes[k].isChecked()]
    if shown != main.show_centers:
        problems.append(
            f"show-center checkboxes {shown} != show_centers {main.show_centers}"
        )
    if main.has_img:
        shape = main.channels[0].shape
        if not main.centers.are_in_img(shape):
            problems.append("a center is outside the image")
        for point, center in main.centers.items():
            names = [r.name for r in main.regions if r.contains(point)]
            expected_region = names[0] if names else ""
            if center.region != expected_region:
                problems.append(
                    f"center {point} has region {center.region!r}, "
                    f"expected {expected_region!r}"
                )
    return problems


def snapshot(main: MainWindow) -> dict[str, object]:
    """Everything about ``main`` that a user can see or that gets saved."""
    return {
        "state": main.state,
        "origin": main.origin,
        "centers": {
            point: (center.color, center.region)
            for point, center in main.centers.items()
        },
        "regions": [(region.name, list(region.points)) for region in main.regions],
        "current_region": (
            None if main.current_region is None else list(main.current_region.points)
        ),
        "colors": dict(main.colors),
        "show_centers": list(main.show_centers),
        "center_colors": main.center_colors,
        "enable_tooltip": main.enable_tooltip,
        "has_img": main.has_img,
        "filename": main.filename,
        "title": main.windowTitle(),
        "buttons": {name: button.text() for name, button in main.button_states.items()},
        "color_checkboxes": [box.isChecked() for box in main.mouse_colors],
        "channel_checkboxes": [
            (box.isChecked(), box.isEnabled()) for box in main.show_channels
        ],
        "show_center_checkboxes": [
            box.isChecked() for box in main.show_center_checkboxes
        ],
        "brightness": list(main.channels.brightness),
        "brightness_enabled": [slider.isEnabled() for slider in main.brightness],
        "zoom": main.zoom.value(),
        "center_size": main.center_size_slider.value(),
    }


def changed(before: dict[str, object], after: dict[str, object]) -> set[str]:
    """The keys of two snapshots whose values differ."""
    return {key for key in before if before[key] != after[key]}


def region_pixels(
    main: MainWindow, points: list[tuple[int, int]]
) -> list[tuple[int, int]]:
    """The pixels of a finished region drawn by clicking ``points``."""
    pixels = [pixel_at(main, point) for point in points]
    return [*pixels, pixels[0]]
