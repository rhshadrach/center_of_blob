from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import pytestqt.qtbot

import cellcensus as cc
from tests import actions


def test_load_csv(monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.load_csv(monkeypatch, qtbot, main, "data/sample.csv")
    assert main.origin == (246, 500)
    assert {point: center.color for point, center in main.centers.items()} == {
        (96, 316): (255, 0, 0),
        (201, 860): (255, 0, 0),
    }
    assert main.regions == []


def test_write_csv(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot, tmp_path: Path
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    main.origin = (50, 50)
    main.centers = cc.Centers({(20, 30): cc.Center(20, 30, (255, 0, 0), "")})
    path = tmp_path / "out.csv"
    actions.save_csv(monkeypatch, qtbot, main, str(path))
    result = pd.read_csv(path)
    expected = pd.DataFrame(
        {
            "kind": ["origin", "center"],
            "x": [50, 20],
            "y": [50, 30],
            "distance": [0.0, 36.055513],
            "red": [0, 255],
            "green": [0, 0],
            "blue": [0, 0],
            "region": [np.nan, np.nan],
        }
    )
    pd.testing.assert_frame_equal(result, expected)


def test_write_csv_regions(
    monkeypatch: pytest.MonkeyPatch, qtbot: pytestqt.qtbot.QtBot, tmp_path: Path
) -> None:
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    main.origin = (50, 50)
    main.centers = cc.Centers({(20, 30): cc.Center(20, 30, (255, 0, 0), "")})
    main.regions = [cc.Region([(10, 10), (10, 40), (40, 40), (40, 10)], "test_name")]
    path = tmp_path / "out.csv"
    actions.save_csv(monkeypatch, qtbot, main, str(path))
    result = pd.read_csv(path)
    expected = pd.DataFrame(
        {
            "kind": ["origin", "center"] + 4 * ["region"],
            "x": [50, 20, 10, 10, 40, 40],
            "y": [50, 30, 10, 40, 40, 10],
            "distance": [0.0, 36.055513, -1.0, -1.0, -1.0, -1.0],
            "red": [0, 255, 255, 255, 255, 255],
            "green": [0, 0, 69, 69, 69, 69],
            "blue": [0, 0, 0, 0, 0, 0],
            "region": [np.nan, np.nan] + 4 * ["test_name"],
        }
    )
    pd.testing.assert_frame_equal(result, expected)
