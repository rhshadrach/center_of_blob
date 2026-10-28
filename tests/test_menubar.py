import pytest
import pytestqt.qtbot
from PyQt5.QtWidgets import QAction, QMessageBox

from tests import actions


def test_info_shows_filename(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    message_boxes: list[QMessageBox],
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    child = main.findChild(QAction, "action_show_info")
    assert child is not None
    child.trigger()
    (box,) = message_boxes
    assert box.text() == f"Filename: {main.filename}"


def test_shortcuts_lists_ctrl_shortcuts(
    qtbot: pytestqt.qtbot.QtBot, message_boxes: list[QMessageBox]
) -> None:
    main = actions.setup_test(qtbot)
    child = main.findChild(QAction, "action_show_shortcuts")
    assert child is not None
    child.trigger()
    (box,) = message_boxes
    for line in [
        "Ctrl+S: Toggle showing red centers",
        "Ctrl+D: Toggle showing green centers",
        "Ctrl+F: Toggle showing blue centers",
    ]:
        assert line in box.text()
