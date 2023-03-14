import tempfile

import numpy as np
import pandas as pd

from center_of_blob.centers import Center
from tests import actions


def test_load_csv(monkeypatch, qtbot):
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    actions.load_csv(monkeypatch, qtbot, main, "data/sample.csv")
    assert len(main.centers) == 2


def test_write_csv(monkeypatch, qtbot):
    main = actions.setup_test(qtbot)
    actions.load_image(monkeypatch, qtbot, main, "data/sample.tif")
    main.origin = (50, 50)
    main.centers = {(20, 30): Center(20, 30, (255, 0, 0), "")}
    with tempfile.NamedTemporaryFile() as file:
        actions.save_csv(monkeypatch, qtbot, main, file.name)
        result = pd.read_csv(file.name)
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
