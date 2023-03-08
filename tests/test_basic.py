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
    expected = {(21, 26): Center(x=21, y=26, color=(255, 0, 0), region="")}
    assert main.centers == expected

    actions.click_color_channel(qtbot, main, channel=2)
    actions.click_main_image(qtbot, main, [(20, 20)])
    expected[(43, 52)] = Center(x=43, y=52, color=(255, 255, 0), region="")
    assert main.centers == expected

    actions.click_color_channel(qtbot, main, channel=1)
    actions.click_main_image(qtbot, main, [(30, 30)])
    expected[(64, 78)] = Center(x=64, y=78, color=(0, 255, 0), region="")
    assert main.centers == expected

    actions.click_color_channel(qtbot, main, channel=3)
    actions.click_main_image(qtbot, main, [(40, 40)])
    expected[(86, 105)] = Center(x=86, y=105, color=(0, 255, 255), region="")
    assert main.centers == expected


def test_add_origin(qtbot, monkeypatch):
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.click_set_origin(qtbot, main)
    assert main.state == "setting_origin"

    # TODO: How to translate (10, 10) to the correct x/y?
    actions.click_main_image(qtbot, main, [(10, 10)])
    assert main.origin == (21, 26)
    assert main.state == "none"


def test_window_title_filename(qtbot, monkeypatch):
    filename = "data/sample.tif"
    main = actions.setup_test(qtbot)
    assert main.windowTitle() == "Center of Blob - No File Loaded"

    actions.load_image(monkeypatch, qtbot, main, filename)
    path = data.resolve_path(filename)
    assert main.filename == path
    assert main.windowTitle() == "Center of Blob - sample.tif"
