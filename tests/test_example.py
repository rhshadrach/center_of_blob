"""The example image and centers file in examples/ load without errors."""

from pathlib import Path

import pytest
import pytestqt.qtbot

from tests import actions

EXAMPLES = Path(__file__).parent.parent / "examples"
NAME = "SC 20x Pax2-NeuN-Sall3 GS.01 1A s02"


def test_example_loads(
    monkeypatch: pytest.MonkeyPatch,
    qtbot: pytestqt.qtbot.QtBot,
    error_messages: list[str],
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, str(EXAMPLES / f"{NAME}.tif"))
    actions.load_csv(monkeypatch, qtbot, main, str(EXAMPLES / f"{NAME}.csv"))
    assert error_messages == []
    assert main.origin == (2203, 2797)
    assert len(main.centers) == 1485
    assert [region.name for region in main.regions] == [
        "Dorsal",
        "Intermediate",
        "Ventral",
    ]
    assert actions.check_invariants(main) == []
