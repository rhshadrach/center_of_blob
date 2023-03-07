from center_of_blob.centers import Center
from tests import actions, data


def test_basic(qtbot):
    main = actions.setup_test(qtbot)
    assert not main.has_img


def test_click_color_channel(qtbot, monkeypatch):
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


def test_add_centers(qtbot, monkeypatch):
    # TODO: Active colors starts as (0, 0, 0)?
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.click_modify_centers(qtbot, main)

    # TODO: Compute expected coordinates
    # Compute based on starting window size
    actions.click_color_channel(qtbot, main, channel=1)
    actions.click_main_image(qtbot, main, [(10, 10)])
    expected_local = {(30, 165): Center(x=30, y=165, color=(255, 0, 0), region="")}
    expected_ci = {(28, 181): Center(x=28, y=181, color=(255, 0, 0), region="")}
    assert main.centers == expected_local or main.centers == expected_ci

    actions.click_color_channel(qtbot, main, channel=2)
    actions.click_main_image(qtbot, main, [(20, 20)])
    expected_local[(60, 330)] = Center(x=60, y=330, color=(255, 255, 0), region="")
    expected_ci[(28 * 2, 181 * 2)] = Center(
        x=28 * 2, y=181 * 2, color=(255, 255, 0), region=""
    )
    assert main.centers == expected_local or main.centers == expected_ci

    actions.click_color_channel(qtbot, main, channel=1)
    actions.click_main_image(qtbot, main, [(30, 30)])
    expected_local[(90, 495)] = Center(x=90, y=495, color=(0, 255, 0), region="")
    expected_ci[(28 * 3, 181 * 3)] = Center(
        x=28 * 3, y=181 * 3, color=(0, 255, 0), region=""
    )
    assert main.centers == expected_local or main.centers == expected_ci

    actions.click_color_channel(qtbot, main, channel=3)
    actions.click_main_image(qtbot, main, [(40, 40)])
    expected_local[(120, 660)] = Center(x=120, y=660, color=(0, 255, 255), region="")
    expected_ci[(28 * 4, 181 * 4)] = Center(
        x=28 * 4, y=181 * 4, color=(0, 255, 255), region=""
    )
    assert main.centers == expected_local or main.centers == expected_ci


def test_add_origin(qtbot, monkeypatch):
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.click_set_origin(qtbot, main)
    assert main.state == "setting_origin"

    # TODO: How to translate (10, 10) to the correct x/y?
    actions.click_main_image(qtbot, main, [(10, 10)])
    assert main.origin == (30, 165) or main.origin == (28, 181)
    assert main.state == "none"


def test_window_title_filename(qtbot, monkeypatch):
    filename = "data/sample.tif"
    main = actions.setup_test(qtbot)
    assert main.windowTitle() == "Center of Blob - No File Loaded"

    actions.load_image(monkeypatch, qtbot, main, filename)
    path = data.resolve_path(filename)
    assert main.filename == path
    assert main.windowTitle() == "Center of Blob - sample.tif"
