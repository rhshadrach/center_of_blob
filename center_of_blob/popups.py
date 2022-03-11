from PyQt5.QtWidgets import QMessageBox


def error_msg(msg):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Critical)
    msgBox.setText(msg)
    msgBox.setWindowTitle("Error!")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()
