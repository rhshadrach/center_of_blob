from tests import actions


def test_load_image(qtbot, monkeypatch):
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    assert main.has_img
    assert main.filename == "/home/richard/dev/center_of_blob/tests/data/sample.tif"
    assert len(main.centers) == 0


def test_failed_image(qtbot, monkeypatch):
    main = actions.setup_test(qtbot)

    actions.setup_close_message_box(qtbot)
    with actions.setup_close_message_box(qtbot):
        actions.load_image(monkeypatch, qtbot, main, "invalid_file.png")
    assert main.filename is None

    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    assert main.filename == "/home/richard/dev/center_of_blob/tests/data/sample.tif"

    with actions.setup_close_message_box(qtbot):
        actions.load_image(monkeypatch, qtbot, main, "invalid_file.png")
    assert main.filename == "/home/richard/dev/center_of_blob/tests/data/sample.tif"
