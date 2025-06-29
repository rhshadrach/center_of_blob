from tests import actions, data
import pytest
import pytestqt


def test_basic(qtbot):
    main = actions.setup_test(qtbot)
    assert not main.has_img


def test_click_color_channel(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.click_modify_centers(qtbot, main)

    assert main.colors == {0: False, 1: False, 2: False}

    actions.click_color_channel(qtbot, main, channel=1)
    assert main.colors == {0: True, 1: False, 2: False}

    actions.click_color_channel(qtbot, main, channel=2)
    assert main.colors == {0: True, 1: True, 2: False}

    actions.click_color_channel(qtbot, main, channel=3)
    assert main.colors == {0: True, 1: True, 2: True}

    actions.click_color_channel(qtbot, main, channel=1)
    assert main.colors == {0: False, 1: True, 2: True}

    actions.click_color_channel(qtbot, main, channel=3)
    assert main.colors == {0: False, 1: True, 2: False}

    actions.click_color_channel(qtbot, main, channel=1)
    assert main.colors == {0: True, 1: True, 2: False}


def test_window_title_filename(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    filename = "data/sample.tif"
    main = actions.setup_test(qtbot)
    assert main.windowTitle() == "Center of Blob - No File Loaded"

    actions.load_image(monkeypatch, qtbot, main, filename)
    path = data.resolve_path(filename)
    assert main.filename == path
    assert main.windowTitle() == "Center of Blob - sample.tif"
