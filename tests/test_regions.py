from PyQt5 import QtCore

from center_of_blob.centers import Center
from tests import actions


def test_make_region_first(qtbot, monkeypatch):
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")

    actions.click_draw_region(qtbot, main)
    actions.click_main_image(qtbot, main, [(90, 90)])
    actions.click_main_image(qtbot, main, [(110, 90)])
    actions.click_main_image(qtbot, main, [(110, 110)])
    actions.click_main_image(qtbot, main, [(90, 110)])
    with actions.setup_close_region_name_box(qtbot, "test_name"):
        actions.click_draw_region(qtbot, main)

    actions.click_modify_centers(qtbot, main)
    actions.click_color_channel(qtbot, main, channel=1)
    actions.click_main_image(qtbot, main, [(100, 100)])
    actions.click_main_image(qtbot, main, [(200, 200)])

    expected = {
        (216, 263): Center(x=216, y=263, color=(255, 0, 0), region="test_name"),
        (432, 526): Center(x=432, y=526, color=(255, 0, 0), region=""),
    }
    assert main.centers == expected


def test_make_region_after(qtbot, monkeypatch):
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")

    actions.click_modify_centers(qtbot, main)
    actions.click_color_channel(qtbot, main, channel=1)
    actions.click_main_image(qtbot, main, [(100, 100)])
    actions.click_main_image(qtbot, main, [(200, 200)])

    actions.click_draw_region(qtbot, main)
    actions.click_main_image(qtbot, main, [(90, 90)])
    actions.click_main_image(qtbot, main, [(110, 90)])
    actions.click_main_image(qtbot, main, [(110, 110)])
    actions.click_main_image(qtbot, main, [(90, 110)])
    with actions.setup_close_region_name_box(qtbot, "test_name"):
        actions.click_draw_region(qtbot, main)

    expected = {
        (216, 263): Center(x=216, y=263, color=(255, 0, 0), region="test_name"),
        (432, 526): Center(x=432, y=526, color=(255, 0, 0), region=""),
    }
    assert main.centers == expected


def test_make_region_overlap_first(qtbot, monkeypatch):
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")

    actions.click_draw_region(qtbot, main)
    actions.click_main_image(qtbot, main, [(90, 90)])
    actions.click_main_image(qtbot, main, [(110, 90)])
    actions.click_main_image(qtbot, main, [(110, 110)])
    actions.click_main_image(qtbot, main, [(90, 110)])
    with actions.setup_close_region_name_box(qtbot, "test_name"):
        actions.click_draw_region(qtbot, main)

    actions.click_draw_region(qtbot, main)
    actions.click_main_image(qtbot, main, [(100, 100)])
    actions.click_main_image(qtbot, main, [(120, 100)])
    actions.click_main_image(qtbot, main, [(120, 120)])
    actions.click_main_image(qtbot, main, [(100, 120)])

    QtCore.QTimer.singleShot(1000, actions.window_accept)
    with actions.setup_close_region_name_box(qtbot, "test_name_2"):
        actions.click_draw_region(qtbot, main)

    actions.click_modify_centers(qtbot, main)
    actions.click_color_channel(qtbot, main, channel=1)
    actions.click_main_image(qtbot, main, [(105, 105)])

    expected = {
        (226, 276): Center(x=226, y=276, color=(255, 0, 0), region="test_name"),
    }
    assert main.centers == expected
