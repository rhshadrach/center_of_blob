from PyQt5.QtWidgets import QAction
import pytest
import pytestqt

from tests import actions

# TODO: Test the output is correct?


def test_info_opens(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    with actions.setup_close_message_box(qtbot):
        main.findChild(QAction, "action_show_info").trigger()
