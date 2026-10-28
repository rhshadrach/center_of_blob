import pytest
import pytestqt.qtbot

from tests import actions, data


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
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    error_messages: list[str],
) -> None:
    filename = "data/sample.tif"
    main = actions.setup_test(qtbot)

    actions.load_image(monkeypatch, qtbot, main, "invalid_file.png")
    assert len(error_messages) == 1
    assert error_messages[0].startswith("Failed to load file")
    assert main.filename is None

    actions.load_image(monkeypatch, qtbot, main, filename)
    assert main.filename == data.resolve_path(filename)

    before = actions.snapshot(main)
    actions.load_image(monkeypatch, qtbot, main, "invalid_file.png")
    assert len(error_messages) == 2
    assert actions.snapshot(main) == before
