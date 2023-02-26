from PyQt5.QtWidgets import QAction

from tests import actions

# TODO: Test the output is correct?


def test_info_opens(qtbot, monkeypatch):
    main = actions.setup_test(qtbot)
    with actions.setup_close_message_box(qtbot):
        main.findChild(QAction, "action_show_info").trigger()
