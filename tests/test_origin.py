import center_of_blob.testing as tm
from tests import actions

import pytest
import pytestqt


def test_add_origin(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.click_set_origin(qtbot, main)
    assert main.state == "setting_origin"

    actions.click_main_image(qtbot, main, [(10, 10)])
    expected = tm.pos_to_pixel((10, 10), main)
    assert main.origin == expected
    assert main.state == "none"


def test_add_origin_outside_image(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.click_set_origin(qtbot, main)
    assert main.state == "setting_origin"

    actions.click_main_image(qtbot, main, [(10000, 10000)])
    assert main.origin is None
    assert main.state == "setting_origin"
