import pytest
import pytestqt.qtbot
from PyQt5.QtCore import Qt

import center_of_blob as cob
from tests import actions


def key_id(value: object) -> str:
    """Name parametrized keys, e.g. ``Key_R``, instead of their key codes."""
    if isinstance(value, Qt.Key):
        return next(
            name
            for name in dir(Qt)
            if name.startswith("Key_") and getattr(Qt, name) == value
        )
    return str(value)


@pytest.mark.parametrize(
    ("key", "channel"),
    [
        (Qt.Key_R, 0),
        (Qt.Key_1, 0),
        (Qt.Key_G, 1),
        (Qt.Key_2, 1),
        (Qt.Key_B, 2),
        (Qt.Key_3, 2),
    ],
    ids=key_id,
)
def test_toggle_drawing_color(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    key: Qt.Key,
    channel: int,
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    before = actions.snapshot(main)

    actions.press_key(monkeypatch, qtbot, main, key)
    after = actions.snapshot(main)
    assert actions.changed(before, after) == {"colors", "color_checkboxes"}
    assert after["colors"] == {k: k == channel for k in range(3)}
    assert after["color_checkboxes"] == [k == channel for k in range(3)]

    actions.press_key(monkeypatch, qtbot, main, key)
    assert actions.snapshot(main) == before


@pytest.mark.parametrize(
    ("key", "channel"),
    [(Qt.Key_A, 0), (Qt.Key_S, 1), (Qt.Key_D, 2), (Qt.Key_F, 3)],
    ids=key_id,
)
def test_toggle_showing_channel(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    key: Qt.Key,
    channel: int,
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    before = actions.snapshot(main)

    actions.press_key(monkeypatch, qtbot, main, key)
    after = actions.snapshot(main)
    assert actions.changed(before, after) == {"channel_checkboxes"}
    assert main.show_channels[channel].isChecked() == (channel != 0)

    actions.press_key(monkeypatch, qtbot, main, key)
    assert actions.snapshot(main) == before


@pytest.mark.parametrize(
    ("key", "channel"), [(Qt.Key_S, 1), (Qt.Key_D, 2), (Qt.Key_F, 3)], ids=key_id
)
def test_ctrl_toggles_show_centers_checkbox(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    key: Qt.Key,
    channel: int,
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    before = actions.snapshot(main)
    checked = main.show_center_checkboxes[channel].isChecked()

    actions.press_key(monkeypatch, qtbot, main, key, ctrl=True)
    assert main.show_center_checkboxes[channel].isChecked() != checked
    # Ctrl changes which centers are shown, not which channels.
    changed = actions.changed(before, actions.snapshot(main))
    assert "show_center_checkboxes" in changed
    assert changed <= {"show_center_checkboxes", "show_centers"}


@pytest.mark.parametrize(
    ("key", "channel"), [(Qt.Key_S, 1), (Qt.Key_D, 2), (Qt.Key_F, 3)], ids=key_id
)
@pytest.mark.xfail(
    reason="The show-centers checkboxes are connected to update_channels, "
    "not update_centers, so they never change which centers are shown",
    strict=True,
)
def test_ctrl_hides_centers_of_channel(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    key: Qt.Key,
    channel: int,
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    assert channel in main.show_centers

    actions.press_key(monkeypatch, qtbot, main, key, ctrl=True)
    assert channel not in main.show_centers


@pytest.mark.parametrize("key", [Qt.Key_Enter, Qt.Key_Return], ids=key_id)
def test_toggle_black_centers(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot, key: Qt.Key
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    before = actions.snapshot(main)
    assert before["center_colors"] == "normal"
    actions.press_key(monkeypatch, qtbot, main, key)
    after = actions.snapshot(main)
    assert actions.changed(before, after) == {"center_colors"}
    assert after["center_colors"] == "black"
    actions.press_key(monkeypatch, qtbot, main, key)
    assert actions.snapshot(main) == before


def test_toggle_tooltip(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    before = actions.snapshot(main)
    assert before["enable_tooltip"]
    actions.press_key(monkeypatch, qtbot, main, Qt.Key_T)
    after = actions.snapshot(main)
    assert actions.changed(before, after) == {"enable_tooltip"}
    assert not after["enable_tooltip"]
    actions.press_key(monkeypatch, qtbot, main, Qt.Key_T)
    assert actions.snapshot(main) == before


def test_debug_information(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    capsys: pytest.CaptureFixture[str],
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    main.centers = cob.Centers({(20, 30): cob.Center(20, 30, (255, 0, 0), "a")})
    actions.press_key(monkeypatch, qtbot, main, Qt.Key_Question)
    out = capsys.readouterr().out
    assert "Coordinates: (20, 30)" in out
    assert "Color: (255, 0, 0)" in out
    assert "Region: a" in out


@pytest.mark.parametrize("key", [Qt.Key_R, Qt.Key_G, Qt.Key_B, Qt.Key_T], ids=key_id)
def test_shortcuts_before_loading_image(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    error_messages: list[str],
    key: Qt.Key,
) -> None:
    main = actions.setup_test(qtbot)
    before = actions.snapshot(main)
    actions.press_key(monkeypatch, qtbot, main, key)
    assert error_messages == []
    assert actions.changed(before, actions.snapshot(main)) <= {
        "colors",
        "color_checkboxes",
        "enable_tooltip",
    }


@pytest.mark.parametrize(
    "key", [Qt.Key_A, Qt.Key_S, Qt.Key_D, Qt.Key_F, Qt.Key_Return], ids=key_id
)
def test_view_shortcuts_before_loading_image(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot, key: Qt.Key
) -> None:
    main = actions.setup_test(qtbot)
    actions.press_key(monkeypatch, qtbot, main, key)
