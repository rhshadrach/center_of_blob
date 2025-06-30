import center_of_blob.testing as tm
from center_of_blob.centers import Center
from tests import actions
import pytest
import pytestqt


def test_add_centers(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    # TODO: Active colors starts as (0, 0, 0)?
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.click_modify_centers(qtbot, main)

    # Compute based on starting window size
    actions.click_color_channel(qtbot, main, channel=1)
    actions.click_main_image(qtbot, main, [(10, 10)])

    pixel = tm.pos_to_pixel((10, 10), main)
    expected = {pixel: Center(x=pixel[0], y=pixel[1], color=(255, 0, 0), region="")}
    assert main.centers == expected

    actions.click_color_channel(qtbot, main, channel=2)
    actions.click_main_image(qtbot, main, [(20, 20)])
    pixel = tm.pos_to_pixel((20, 20), main)
    expected[pixel] = Center(x=pixel[0], y=pixel[1], color=(255, 255, 0), region="")
    assert main.centers == expected

    actions.click_color_channel(qtbot, main, channel=1)
    actions.click_main_image(qtbot, main, [(30, 30)])
    pixel = tm.pos_to_pixel((30, 30), main)
    expected[pixel] = Center(x=pixel[0], y=pixel[1], color=(0, 255, 0), region="")
    assert main.centers == expected

    actions.click_color_channel(qtbot, main, channel=3)
    actions.click_main_image(qtbot, main, [(40, 40)])
    pixel = tm.pos_to_pixel((40, 40), main)
    expected[pixel] = Center(x=pixel[0], y=pixel[1], color=(0, 255, 255), region="")
    assert main.centers == expected


def test_outside_image(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.click_modify_centers(qtbot, main)
    actions.click_color_channel(qtbot, main, channel=1)
    actions.click_main_image(qtbot, main, [(10000, 10000)])
    assert len(main.centers) == 0
