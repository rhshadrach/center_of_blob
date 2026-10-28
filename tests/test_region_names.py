"""Every region needs a non-empty name that no other region has."""

import pytest
import pytestqt.qtbot

from tests import actions

SQUARE = [(90, 90), (110, 90), (110, 110), (90, 110)]
SQUARE_2 = [(190, 190), (210, 190), (210, 210), (190, 210)]


def finish_region(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    main: actions.MainWindow,
    points: list[tuple[int, int]],
    answers: list[tuple[str, bool]],
) -> None:
    """Draw a region, answering the name dialog with each of ``answers``."""
    remaining = actions.answer_region_names(monkeypatch, answers)
    actions.click_draw_region(qtbot, main)
    actions.click_main_image(qtbot, main, points)
    actions.click_draw_region(qtbot, main)
    assert remaining == []


def test_cancel_discards_region(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    error_messages: list[str],
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    before = actions.snapshot(main)
    finish_region(monkeypatch, qtbot, main, SQUARE, [("ignored", False)])
    assert actions.snapshot(main) == before
    assert error_messages == []


@pytest.mark.parametrize("empty", ["", "   "])
def test_empty_name_asks_again(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    error_messages: list[str],
    empty: str,
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    finish_region(monkeypatch, qtbot, main, SQUARE, [(empty, True), ("a", True)])
    assert actions.snapshot(main)["regions"] == [
        ("a", actions.region_pixels(main, SQUARE))
    ]
    assert error_messages == []


def test_empty_name_then_cancel_discards_region(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    finish_region(monkeypatch, qtbot, main, SQUARE, [("", True), ("", False)])
    assert main.regions == []


def test_shared_name_shows_error_and_asks_again(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    error_messages: list[str],
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    finish_region(monkeypatch, qtbot, main, SQUARE, [("a", True)])
    finish_region(monkeypatch, qtbot, main, SQUARE_2, [("a", True), ("b", True)])
    assert error_messages == ["A region named 'a' already exists."]
    assert actions.snapshot(main)["regions"] == [
        ("a", actions.region_pixels(main, SQUARE)),
        ("b", actions.region_pixels(main, SQUARE_2)),
    ]


def test_shared_name_then_cancel_discards_region(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    error_messages: list[str],
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    finish_region(monkeypatch, qtbot, main, SQUARE, [("a", True)])
    before = actions.snapshot(main)
    finish_region(monkeypatch, qtbot, main, SQUARE_2, [("a", True), ("", False)])
    assert error_messages == ["A region named 'a' already exists."]
    assert actions.snapshot(main) == before


def test_cancel_when_switching_modes_discards_region(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    remaining = actions.answer_region_names(monkeypatch, [("ignored", False)])
    actions.click_draw_region(qtbot, main)
    actions.click_main_image(qtbot, main, SQUARE)
    actions.click_modify_centers(qtbot, main)
    assert remaining == []
    assert main.state == "modifying_centers"
    assert main.regions == []
    assert actions.check_invariants(main) == []


def test_region_without_points_does_not_ask_for_name(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    before = actions.snapshot(main)
    finish_region(monkeypatch, qtbot, main, [], [])
    assert actions.snapshot(main) == before
