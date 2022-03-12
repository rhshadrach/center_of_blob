from PyQt5.QtWidgets import QMessageBox, QAction
from PyQt5.QtGui import QIcon

from center_of_blob import __version__


def error_msg(msg):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Critical)
    msgBox.setText(msg)
    msgBox.setWindowTitle("Error!")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()


def about_dialog():
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setText(f'Center Of Blob version {__version__}\nBy Richard Shadrach')
    msgBox.setWindowTitle("About")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()
