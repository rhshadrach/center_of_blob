"""Zoom, center size, channel visibility, brightness and tooltips."""

import warnings

import pytest
import pytestqt.qtbot
from PyQt5.QtCore import Qt

from tests import actions

SQUARE = [(90, 90), (110, 90), (110, 110), (90, 110)]


def test_zoom_slider_scales_image(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    height = main.label.label.pixmap().height()
    main.zoom.setValue(200)
    assert main.label.label.pixmap().height() == 2 * height


def test_ctrl_scroll_zooms(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    before = main.zoom.value()
    actions.ctrl_scroll(monkeypatch, main, 120)
    assert main.zoom.value() == before + 24


def test_add_center_after_zoom(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.click_modify_centers(qtbot, main)
    actions.click_color_channel(qtbot, main, channel=1)
    actions.click_main_image(qtbot, main, [(100, 100)])
    before = actions.pixel_at(main, (100, 100))

    main.zoom.setValue(200)
    # The same image pixel is now twice as far from the corner.
    actions.right_click_main_image(qtbot, main, [(200, 200)])
    assert before not in main.centers


def test_zoom_before_loading_image(
    qtbot: pytestqt.qtbot.QtBot, error_messages: list[str]
) -> None:
    main = actions.setup_test(qtbot)
    main.zoom.setValue(200)
    assert error_messages == ["Must load image first."]


def test_center_size_before_loading_image(
    qtbot: pytestqt.qtbot.QtBot, error_messages: list[str]
) -> None:
    main = actions.setup_test(qtbot)
    main.center_size_slider.setValue(8)
    assert error_messages == ["Must load image first."]


@pytest.mark.parametrize("button", ["centers_path_button", "write_csv_button"])
def test_file_buttons_before_loading_image(
    qtbot: pytestqt.qtbot.QtBot, error_messages: list[str], button: str
) -> None:
    main = actions.setup_test(qtbot)
    qtbot.mouseClick(getattr(main, button), Qt.LeftButton)
    assert error_messages == ["Must load image first."]


@pytest.mark.parametrize("mode", ["set_origin", "modify_centers", "draw_region"])
def test_mode_buttons_before_loading_image(
    qtbot: pytestqt.qtbot.QtBot, error_messages: list[str], mode: str
) -> None:
    main = actions.setup_test(qtbot)
    getattr(actions, f"click_{mode}")(qtbot, main)
    assert error_messages == ["Must load image first."]
    assert main.state == "none"


@pytest.mark.parametrize("channel", [0, 1, 2, 3])
@pytest.mark.xfail(
    reason="Toggling a channel redraws the image without checking one is loaded, "
    "raising IndexError",
    strict=True,
)
def test_toggle_channel_before_loading_image(
    qtbot: pytestqt.qtbot.QtBot, channel: int
) -> None:
    main = actions.setup_test(qtbot)
    qtbot.mouseClick(main.show_channels[channel], Qt.LeftButton)


def test_brightness_boxes_update_channel(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    main.brightness[1].box_low.setValue(40)
    main.brightness[1].box_high.setValue(200)
    assert main.channels.brightness[1] == (40, 200)


@pytest.mark.xfail(
    reason="Equal low and high brightness divides by zero in Channels.clip_data",
    strict=True,
)
def test_brightness_low_equal_to_high(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    main.show_channels[1].setChecked(True)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        main.brightness[1].box_high.setValue(100)
        main.brightness[1].box_low.setValue(100)


def test_tooltip_shows_region_name(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.draw_region(monkeypatch, qtbot, main, SQUARE, "inner")
    actions.move_mouse(main, (100, 100))
    assert main.label.toolTip() == "inner"
    actions.move_mouse(main, (300, 300))
    assert main.label.toolTip() == ""


@pytest.mark.xfail(
    reason="Turning tooltips off with T leaves the last tooltip in place",
    strict=True,
)
def test_disabling_tooltip_clears_it(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.draw_region(monkeypatch, qtbot, main, SQUARE, "inner")
    actions.move_mouse(main, (100, 100))
    actions.press_key(monkeypatch, qtbot, main, Qt.Key_T)
    actions.move_mouse(main, (100, 100))
    assert main.label.toolTip() == ""


@pytest.mark.xfail(
    reason="Show-centers checkboxes start unchecked while all centers are shown",
    strict=True,
)
def test_show_centers_checkboxes_match_at_startup(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    shown = [k for k in range(1, 4) if main.show_center_checkboxes[k].isChecked()]
    assert shown == main.show_centers
