"""Adding and removing centers, origins and regions, including at the edges."""

import numpy as np
import pytest
import pytestqt.qtbot
from PIL import Image

from center_of_blob import analyze
from center_of_blob.centers import Center
from tests import actions


def bottom_right(main: actions.MainWindow) -> tuple[int, int]:
    pixmap = main.label.label.pixmap()
    return pixmap.width() - 1, pixmap.height() - 1


def test_click_maps_x_to_column(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.click_modify_centers(qtbot, main)
    actions.click_color_channel(qtbot, main, channel=1)
    actions.click_main_image(qtbot, main, [(300, 20)])
    assert list(main.centers) == [actions.pixel_at(main, (300, 20))]
    ((row, column),) = main.centers
    # Pixels are (row, column): clicking far right and near the top gives a
    # small row and a large column.
    assert row < column


def test_click_near_center_merges_colors(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.click_modify_centers(qtbot, main)
    actions.click_color_channel(qtbot, main, channel=1)
    actions.click_main_image(qtbot, main, [(100, 100)])
    actions.click_color_channel(qtbot, main, channel=1)
    actions.click_color_channel(qtbot, main, channel=2)
    actions.click_main_image(qtbot, main, [(101, 101)])

    pixel = actions.pixel_at(main, (100, 100))
    assert main.centers == {
        pixel: Center(x=pixel[0], y=pixel[1], color=(255, 255, 0), region="")
    }


def test_click_without_color_adds_nothing(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.click_modify_centers(qtbot, main)
    before = actions.snapshot(main)
    actions.click_main_image(qtbot, main, [(100, 100)])
    assert actions.snapshot(main) == before


def test_click_outside_mode_adds_nothing(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.click_color_channel(qtbot, main, channel=1)
    before = actions.snapshot(main)
    actions.click_main_image(qtbot, main, [(100, 100)])
    assert actions.snapshot(main) == before


def test_right_click_removes_nearest_center(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.click_modify_centers(qtbot, main)
    actions.click_color_channel(qtbot, main, channel=1)
    actions.click_main_image(qtbot, main, [(100, 100), (120, 120)])
    actions.right_click_main_image(qtbot, main, [(104, 104)])
    assert list(main.centers) == [actions.pixel_at(main, (120, 120))]


def test_right_click_far_from_centers_removes_nothing(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.click_modify_centers(qtbot, main)
    actions.click_color_channel(qtbot, main, channel=1)
    actions.click_main_image(qtbot, main, [(100, 100)])
    before = actions.snapshot(main)
    actions.right_click_main_image(qtbot, main, [(300, 300)])
    assert actions.snapshot(main) == before


def test_set_origin_twice_moves_it(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    for pos in [(50, 50), (200, 100)]:
        actions.click_set_origin(qtbot, main)
        actions.click_main_image(qtbot, main, [pos])
    assert main.origin == actions.pixel_at(main, (200, 100))


def test_region_with_too_few_points_contains_nothing(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.draw_region(monkeypatch, qtbot, main, [(90, 90), (110, 110)], "line")
    actions.click_modify_centers(qtbot, main)
    actions.click_color_channel(qtbot, main, channel=1)
    actions.click_main_image(qtbot, main, [(100, 100)])
    assert [center.region for center in main.centers.values()] == [""]


@pytest.mark.xfail(
    reason="Drawing a center near the bottom or right edge indexes past the image",
    strict=True,
)
def test_add_center_at_bottom_right(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.click_modify_centers(qtbot, main)
    actions.click_color_channel(qtbot, main, channel=1)
    actions.click_main_image(qtbot, main, [bottom_right(main)])
    assert len(main.centers) == 1


@pytest.mark.xfail(
    reason="Drawing the origin near the bottom or right edge indexes past the image",
    strict=True,
)
def test_set_origin_at_bottom_right(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.click_set_origin(qtbot, main)
    actions.click_main_image(qtbot, main, [bottom_right(main)])
    assert main.origin is not None


@pytest.mark.xfail(
    reason="Drawing a point near the top or left edge wraps onto the opposite "
    "edges through negative indexing",
    strict=True,
)
def test_highlight_point_at_top_left_does_not_wrap() -> None:
    data = np.zeros((40, 50, 3), dtype="uint8")
    analyze.highlight_point(data, (0, 0), (255, 0, 0), center_size=5)
    assert data[-1, -1].tolist() == [0, 0, 0]
    assert data[-1, 0].tolist() == [0, 0, 0]
    assert data[0, -1].tolist() == [0, 0, 0]


def three_frame_tiff(path: str) -> None:
    frames = [Image.fromarray(np.full((40, 50), v, dtype="uint8")) for v in (1, 2, 3)]
    frames[0].save(path, save_all=True, append_images=frames[1:])


def test_three_frame_image_disables_channel_0(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot, tmp_path
) -> None:
    path = str(tmp_path / "three.tif")
    three_frame_tiff(path)
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, path)
    assert not main.show_channels[0].isEnabled()
    assert not main.show_channels[0].isChecked()
    assert not main.brightness[0].isEnabled()

    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    assert main.show_channels[0].isEnabled()
    assert main.brightness[0].isEnabled()


def test_non_tiff_image_is_refused(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    tmp_path,
    error_messages: list[str],
) -> None:
    path = str(tmp_path / "image.png")
    Image.fromarray(np.zeros((40, 50), dtype="uint8")).save(path)
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    before = actions.snapshot(main)
    actions.load_image(monkeypatch, qtbot, main, path)
    assert len(error_messages) == 1
    assert error_messages[0].startswith("Failed to load file")
    assert actions.snapshot(main) == before


@pytest.mark.xfail(
    reason="Cancelling the image dialog tries to open the current directory and "
    "shows an error",
    strict=True,
)
def test_cancel_image_dialog(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    error_messages: list[str],
) -> None:
    main = actions.setup_test(qtbot)
    before = actions.snapshot(main)
    monkeypatch.setattr(actions.popups, "get_image_filename", lambda *a, **k: "")
    qtbot.mouseClick(main.img_path_button, actions.QtCore.Qt.LeftButton)
    assert error_messages == []
    assert actions.snapshot(main) == before
