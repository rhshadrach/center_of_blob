import pytest
from PyQt5.QtWidgets import QMessageBox

from center_of_blob import popups


@pytest.fixture
def error_messages(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Record error popups instead of showing them."""
    messages: list[str] = []
    monkeypatch.setattr(popups, "error_msg", messages.append)
    return messages


@pytest.fixture
def message_boxes(monkeypatch: pytest.MonkeyPatch) -> list[QMessageBox]:
    """Record message boxes instead of showing them."""
    boxes: list[QMessageBox] = []

    def exec_(box: QMessageBox) -> None:
        boxes.append(box)

    monkeypatch.setattr(QMessageBox, "exec", exec_)
    return boxes
