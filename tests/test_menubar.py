import pytest
import pytestqt.qtbot
from PyQt5.QtWidgets import QAction, QMessageBox

from tests import actions

# TODO: Test the output is correct?


def test_info_opens(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    with actions.setup_close_message_box(qtbot):
        child = main.findChild(QAction, "action_show_info")
        assert child is not None
        child.trigger()


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
