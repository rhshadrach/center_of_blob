import pytest
import pytestqt

from tests import actions


@pytest.mark.parametrize("channel", [0, 1, 2, 3])
@pytest.mark.parametrize("load_first", [True, False])
@pytest.mark.parametrize("adjust_low", [True, False])
def test_adjust_brightness(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    channel: int,
    load_first: bool,
    adjust_low: bool,
) -> None:
    expected = {
        0: (0, 255),
        1: (0, 255),
        2: (0, 255),
        3: (0, 255),
    }
    main = actions.setup_test(qtbot)
    assert main.channels.brightness == list(expected.values())

    if load_first:
        actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")

    value = 150
    if adjust_low:
        main.brightness[channel].setLow(value)
        expected[channel] = (value, expected[channel][1])
    else:
        main.brightness[channel].setHigh(value)
        expected[channel] = (expected[channel][0], value)

    if not load_first:
        actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")

    assert main.channels.brightness == list(expected.values())
