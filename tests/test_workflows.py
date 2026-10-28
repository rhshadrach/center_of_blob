"""Sequences of user actions, checking the window's state after every step."""

import itertools

import pytest
import pytestqt.qtbot

from tests import actions

SQUARE = [(90, 90), (110, 90), (110, 110), (90, 110)]
SQUARE_2 = [(190, 190), (210, 190), (210, 210), (190, 210)]


def assert_consistent(main: actions.MainWindow) -> None:
    assert actions.check_invariants(main) == []


def test_invariants_hold_at_startup(qtbot: pytestqt.qtbot.QtBot) -> None:
    main = actions.setup_test(qtbot)
    assert_consistent(main)


def test_full_session(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    error_messages: list[str],
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    assert_consistent(main)

    actions.click_set_origin(qtbot, main)
    actions.click_main_image(qtbot, main, [(50, 50)])
    assert main.origin == actions.pixel_at(main, (50, 50))
    assert_consistent(main)

    actions.draw_region(monkeypatch, qtbot, main, SQUARE, "inner")
    actions.draw_region(monkeypatch, qtbot, main, SQUARE_2, "outer")
    assert [region.name for region in main.regions] == ["inner", "outer"]
    assert_consistent(main)

    actions.click_modify_centers(qtbot, main)
    actions.click_color_channel(qtbot, main, channel=1)
    actions.click_main_image(qtbot, main, [(100, 100), (200, 200), (300, 300)])
    assert_consistent(main)
    actions.right_click_main_image(qtbot, main, [(300, 300)])
    actions.click_modify_centers(qtbot, main)
    assert_consistent(main)

    regions = {
        actions.pixel_at(main, pos): center.region
        for pos, center in zip([(100, 100), (200, 200)], main.centers.values())
    }
    assert sorted(regions.values()) == ["inner", "outer"]
    assert len(main.centers) == 2
    assert error_messages == []


@pytest.mark.parametrize(
    "order", list(itertools.permutations(["origin", "region", "centers"]))
)
def test_order_of_actions_does_not_matter(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    order: tuple[str, ...],
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    for step in order:
        if step == "origin":
            actions.click_set_origin(qtbot, main)
            actions.click_main_image(qtbot, main, [(50, 50)])
        elif step == "region":
            actions.draw_region(monkeypatch, qtbot, main, SQUARE, "inner")
        else:
            actions.click_modify_centers(qtbot, main)
            actions.click_color_channel(qtbot, main, channel=2)
            actions.click_main_image(qtbot, main, [(100, 100), (300, 300)])
            actions.click_color_channel(qtbot, main, channel=2)
            actions.click_modify_centers(qtbot, main)
        assert_consistent(main)

    assert main.origin == actions.pixel_at(main, (50, 50))
    assert [region.name for region in main.regions] == ["inner"]
    assert {
        point: (center.color, center.region) for point, center in main.centers.items()
    } == {
        actions.pixel_at(main, (100, 100)): ((0, 255, 0), "inner"),
        actions.pixel_at(main, (300, 300)): ((0, 255, 0), ""),
    }


@pytest.mark.parametrize("start", ["set_origin", "modify_centers", "draw_region"])
@pytest.mark.parametrize("then", ["set_origin", "modify_centers", "draw_region"])
def test_switching_modes(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    start: str,
    then: str,
) -> None:
    buttons = {
        "set_origin": actions.click_set_origin,
        "modify_centers": actions.click_modify_centers,
        "draw_region": actions.click_draw_region,
    }
    states = {
        "set_origin": "setting_origin",
        "modify_centers": "modifying_centers",
        "draw_region": "drawing_region",
    }
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    buttons[start](qtbot, main)
    assert main.state == states[start]
    assert_consistent(main)

    buttons[then](qtbot, main)
    assert main.state == ("none" if start == then else states[then])
    assert_consistent(main)


def test_switching_mode_finishes_region(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    monkeypatch.setattr(
        actions.QInputDialog, "getText", lambda *args: ("switched", True)
    )
    actions.click_draw_region(qtbot, main)
    actions.click_main_image(qtbot, main, SQUARE)
    actions.click_modify_centers(qtbot, main)

    assert main.state == "modifying_centers"
    assert [region.name for region in main.regions] == ["switched"]
    assert_consistent(main)


def test_remove_region_reclassifies_centers(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.draw_region(monkeypatch, qtbot, main, SQUARE, "inner")
    actions.click_modify_centers(qtbot, main)
    actions.click_color_channel(qtbot, main, channel=1)
    actions.click_main_image(qtbot, main, [(100, 100)])
    actions.click_modify_centers(qtbot, main)
    assert [center.region for center in main.centers.values()] == ["inner"]

    # Right-clicking near a region's corner outside any mode removes it.
    actions.right_click_main_image(qtbot, main, [(91, 91)])
    assert main.regions == []
    assert [center.region for center in main.centers.values()] == [""]
    assert_consistent(main)


def test_right_click_away_from_region_keeps_it(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.draw_region(monkeypatch, qtbot, main, SQUARE, "inner")
    actions.right_click_main_image(qtbot, main, [(400, 400)])
    assert [region.name for region in main.regions] == ["inner"]


def test_right_click_in_modify_mode_removes_center_not_region(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.draw_region(monkeypatch, qtbot, main, SQUARE, "inner")
    actions.click_modify_centers(qtbot, main)
    actions.click_color_channel(qtbot, main, channel=1)
    actions.click_main_image(qtbot, main, [(91, 91)])
    actions.right_click_main_image(qtbot, main, [(91, 91)])
    assert len(main.centers) == 0
    assert [region.name for region in main.regions] == ["inner"]


def test_loading_new_image_resets_work(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.click_set_origin(qtbot, main)
    actions.click_main_image(qtbot, main, [(50, 50)])
    actions.draw_region(monkeypatch, qtbot, main, SQUARE, "inner")
    actions.click_modify_centers(qtbot, main)
    actions.click_color_channel(qtbot, main, channel=1)
    actions.click_main_image(qtbot, main, [(100, 100)])
    actions.click_modify_centers(qtbot, main)

    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    assert main.origin is None
    assert main.regions == []
    assert len(main.centers) == 0


@pytest.mark.parametrize("mode", ["set_origin", "modify_centers", "draw_region"])
@pytest.mark.xfail(
    reason="Loading an image resets the mode but not the mode buttons' text",
    strict=True,
)
def test_loading_image_mid_mode_resets_buttons(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot, mode: str
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    getattr(actions, f"click_{mode}")(qtbot, main)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    assert main.state == "none"
    assert_consistent(main)


@pytest.mark.xfail(
    reason="Loading an image clears the drawing colors but not their checkboxes",
    strict=True,
)
def test_loading_image_keeps_color_checkboxes_in_sync(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.click_color_channel(qtbot, main, channel=1)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    assert_consistent(main)


@pytest.mark.xfail(
    reason="Loading a centers file mid-region clears the region but not the mode",
    strict=True,
)
def test_loading_centers_while_drawing_region(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.click_draw_region(qtbot, main)
    actions.click_main_image(qtbot, main, [(90, 90)])
    actions.load_csv(monkeypatch, qtbot, main, "data/sample.csv")
    assert_consistent(main)
    # Continuing to draw must not fail.
    actions.click_main_image(qtbot, main, [(110, 90)])
