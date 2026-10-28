from pathlib import Path

import pytest
import pytestqt.qtbot

from cellcensus import popups
from cellcensus.smoke_test import smoke_test

EXAMPLE = (
    Path(__file__).parent.parent / "examples" / "SC 20x Pax2-NeuN-Sall3 GS.01 1A s02"
)


def test_smoke_test_passes_on_example(
    qtbot: pytestqt.qtbot.QtBot, capsys: pytest.CaptureFixture[str]
) -> None:
    error_msg = popups.error_msg
    assert smoke_test(f"{EXAMPLE}.tif", f"{EXAMPLE}.csv") == 0
    assert capsys.readouterr().out == "Smoke test passed: 1485 centers in 3 regions.\n"
    # The smoke test restores what it patched.
    assert popups.error_msg is error_msg


def test_smoke_test_reports_first_problem(
    qtbot: pytestqt.qtbot.QtBot,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    path = tmp_path / "outside.csv"
    path.write_text(
        "kind,x,y,distance,red,green,blue,region\n"
        "origin,10,10,0.0,0,0,0,\n"
        "center,99999,10,5.0,255,0,0,\n"
    )
    assert smoke_test(f"{EXAMPLE}.tif", str(path)) == 1
    assert capsys.readouterr().err == (
        "Smoke test failed: "
        "Centers file has points outside of image bounds. Refusing file.\n"
    )
