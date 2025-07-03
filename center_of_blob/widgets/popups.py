from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QMainWindow

from center_of_blob import __version__

if TYPE_CHECKING:
    from center_of_blob.main import MainWindow


def error_msg(msg: str) -> None:
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Critical)
    msgBox.setText(msg)
    msgBox.setWindowTitle("Error!")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()


def info_dialog(main_window: MainWindow) -> None:
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setText(f"Filename: {main_window.filename}")
    msgBox.setWindowTitle("Info")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()


def shortcuts_dialog(main_window: MainWindow) -> None:
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setText(
        "Shortcuts:\n"
        "R or 1: Toggle coloring red channel\n"
        "G or 2: Toggle coloring green channel\n"
        "B or 3: Toggle coloring blue channel\n"
        "A: Toggle showing channel 0\n"
        "S: Toggle showing red channel\n"
        "D: Toggle showing green channel\n"
        "F: Toggle showing blue channel\n"
        "Enter or Return: Toggle coloring all centers black\n"
        "T: Toggle mouse tooltip\n"
        "?: Print debug information to console\n"
    )
    msgBox.setWindowTitle("Shortcuts")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()


def about_dialog() -> None:
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setText(f"Center Of Blob version {__version__}\nBy Richard Shadrach")
    msgBox.setWindowTitle("About")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()


def get_image_filename(main_window: QMainWindow, directory: str) -> str:
    result = QtWidgets.QFileDialog.getOpenFileName(
        parent=main_window, caption="Open Image File", directory=directory
    )[0]
    return result


def get_csv_save_filename(main_window: QMainWindow, directory: str) -> str:
    result = QtWidgets.QFileDialog.getSaveFileName(
        parent=main_window, caption="Choose CSV filename", directory=directory
    )[0]
    return result


def get_centers_filename(main_window: QMainWindow, directory: str) -> str:
    result = QtWidgets.QFileDialog.getOpenFileName(
        parent=main_window, caption="Open Centers File", directory=directory
    )[0]
    return result
