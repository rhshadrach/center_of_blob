import pytest

from center_of_blob.main import QLabelDemo
from center_of_blob.popups import ImageNameDialog, CentersFileDialog


@pytest.fixture
def main(qtbot, monkeypatch):
    monkeypatch.setattr(
        ImageNameDialog, "getOpenFileName", classmethod(lambda *args: "data/sample.tif")
    )
    monkeypatch.setattr(
        CentersFileDialog, "getOpenFileName", classmethod(lambda *args: "data/sample.csv")
    )
    main = QLabelDemo()
    main.get_img_file()
    return main
