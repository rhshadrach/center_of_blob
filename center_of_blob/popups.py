from __future__ import annotations
from __future__ import annotations

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from center_of_blob import __version__


def error_msg(msg):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Critical)
    msgBox.setText(msg)
    msgBox.setWindowTitle("Error!")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()


def info_dialog(obj):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setText(f"Filename: {obj.filename}")
    msgBox.setWindowTitle("Info")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()


def shortcuts_dialog(obj):
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


def about_dialog():
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setText(f"Center Of Blob version {__version__}\nBy Richard Shadrach")
    msgBox.setWindowTitle("About")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()


class ImageNameDialog(QFileDialog):
    @classmethod
    def getOpenFileName(cls, parent, default_dir):
        result = super().getOpenFileName(
            parent,
            "Open Image File",
            default_dir,
        )
        return result[0]


class CsvNameDialog(QFileDialog):
    @classmethod
    def getSaveFileName(cls, parent, default_dir):
        result = super().getSaveFileName(
            parent,
            "Choose CSV filename",
            default_dir,
        )
        return result[0]


class CsvNameDialog(QFileDialog):
    @classmethod
    def getSaveFileName(cls, parent, default_dir):
        result = super().getSaveFileName(
            parent,
            'Choose CSV filename',
            default_dir,
        )
        return result[0]


class CentersFileDialog(QFileDialog):
    @classmethod
    def getOpenFileName(cls, parent, default_dir):
        result = super().getOpenFileName(
            parent,
            "Open Centers File",
            default_dir,
        )
        return result[0]
