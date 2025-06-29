from tests import actions, data
import pytest
import pytestqt


def test_load_image(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    filename = "data/sample.tif"
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, filename)
    assert main.has_img
    assert main.filename == data.resolve_path(filename)
    assert len(main.centers) == 0


def test_failed_image(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    filename = "data/sample.tif"
    main = actions.setup_test(qtbot)

    actions.setup_close_message_box(qtbot)
    with actions.setup_close_message_box(qtbot):
        actions.load_image(monkeypatch, qtbot, main, "invalid_file.png")
    assert main.filename is None

    actions.load_image(monkeypatch, qtbot, main, filename)
    assert main.filename == data.resolve_path(filename)

    with actions.setup_close_message_box(qtbot):
        actions.load_image(monkeypatch, qtbot, main, "invalid_file.png")
    assert main.filename == data.resolve_path(filename)
