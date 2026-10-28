from pathlib import Path

import pytest
import pytestqt.qtbot

from cellcensus.main import except_hook
from tests import actions, data


def test_basic(qtbot: pytestqt.qtbot.QtBot) -> None:
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
    assert main.windowTitle() == "CellCensus - No File Loaded"

    actions.load_image(monkeypatch, qtbot, main, filename)
    path = data.resolve_path(filename)
    assert main.filename == path
    assert main.windowTitle() == "CellCensus - sample.tif"


def test_except_hook_writes_log(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, error_messages: list[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    try:
        raise ValueError("boom")
    except ValueError as err:
        except_hook(type(err), err, err.__traceback__)
    (log,) = tmp_path.glob("cellcensus_error_*.log")
    # Windows doesn't allow colons in filenames.
    assert ":" not in log.name
    assert "ValueError" in log.read_text()
    assert "boom" in log.read_text()
    assert len(error_messages) == 1
    assert log.name in error_messages[0]
