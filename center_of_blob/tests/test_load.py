def test_load_image(qtbot, main):
    qtbot.addWidget(main)


def test_load_csv(qtbot, main):
    qtbot.addWidget(main)
    main.get_centers_file()
    assert len(main.centers) == 6
