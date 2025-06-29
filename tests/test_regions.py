from PyQt5 import QtCore

import center_of_blob.testing as tm
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

    pixel0 = tm.pos_to_pixel((100, 100), main)
    pixel1 = tm.pos_to_pixel((200, 200), main)
    expected = {
        pixel0: Center(x=pixel0[0], y=pixel0[1], color=(255, 0, 0), region="test_name"),
        pixel1: Center(x=pixel1[0], y=pixel1[1], color=(255, 0, 0), region=""),
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

    pixel0 = tm.pos_to_pixel((100, 100), main)
    pixel1 = tm.pos_to_pixel((200, 200), main)
    expected = {
        pixel0: Center(x=pixel0[0], y=pixel0[1], color=(255, 0, 0), region="test_name"),
        pixel1: Center(x=pixel1[0], y=pixel1[1], color=(255, 0, 0), region=""),
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

    pixel = tm.pos_to_pixel((105, 105), main)
    expected = {
        (pixel[0], pixel[1]): Center(
            x=pixel[0], y=pixel[1], color=(255, 0, 0), region="test_name"
        ),
    }
    assert main.centers == expected
