from PyQt5 import QtCore
from PyQt5.QtWidgets import QCheckBox, QMainWindow, QPushButton, QSlider

from center_of_blob.boxed_range_slider import BoxedRangeSlider
from center_of_blob.main_image import ScrollLabel


def create_img_path_button(main_window: QMainWindow) -> QPushButton:
    result = QPushButton("Select Image File")
    result.clicked.connect(main_window.get_img_file)
    return result


def create_centers_path_button(main_window: QMainWindow) -> QPushButton:
    result = QPushButton("Select Centers File")
    result.clicked.connect(lambda: main_window.get_centers_file())
    return result


def create_set_origin_button(main_window: QMainWindow) -> QPushButton:
    # TODO: Why pass main_window?
    result = QPushButton("Start setting origin", main_window)
    result.setToolTip("Click this button and then click on the desired origin")
    result.resize(150, 50)
    result.clicked.connect(lambda: main_window.activate_set_origin())
    return result


def create_locate_blobs_button(main_window: QMainWindow) -> QPushButton:
    # TODO: Why pass main_window?
    result = QPushButton("Locate blobs", main_window)
    result.setToolTip("Click this button to locate blobs")
    result.resize(150, 50)
    result.clicked.connect(lambda: main_window.locate_blobs())
    return result


def create_modify_centers(main_window: QMainWindow) -> QPushButton:
    # TODO: Why pass main_window?
    result = QPushButton("Start modifying centers", main_window)
    result.resize(150, 50)
    result.clicked.connect(lambda: main_window.activate_modify_centers())
    return result


def create_draw_region(main_window: QMainWindow) -> QPushButton:
    result = QPushButton("Start drawing region", main_window)
    result.resize(150, 50)
    result.clicked.connect(lambda: main_window.activate_drawing_region())
    return result


def create_write_csv_button(main_window: QMainWindow) -> QPushButton:
    result = QPushButton("Write CSV", main_window)
    result.resize(150, 50)
    result.clicked.connect(lambda: main_window.write_csv())
    return result


# TODO: Change to a dict
def create_mouse_colors(main_window: QMainWindow, n_channels: int) -> list[QCheckBox]:
    result = []
    for k in range(1, n_channels):
        check_box = QCheckBox(f"Color Channel {k}")
        check_box.setChecked(False)
        check_box.stateChanged.connect(lambda: main_window.update_mouse_colors())
        result.append(check_box)
    return result


# TODO: Change to a dict
def create_show_channels(main_window: QMainWindow, n_channels: int) -> list[QCheckBox]:
    result = []
    for k in range(n_channels):
        check_box = QCheckBox(f"Channel {k}")
        check_box.setChecked(k == 0)
        check_box.stateChanged.connect(lambda: main_window.update_channels())
        result.append(check_box)
    return result


# TODO: Change to a dict
def create_show_center_checkboxes(
    main_window: QMainWindow, n_channels: int
) -> list[QCheckBox]:
    result = []
    for k in range(n_channels):
        check_box = QCheckBox(f"Channel {k}")
        check_box.setChecked(k == 0)
        check_box.stateChanged.connect(lambda: main_window.update_channels())
        result.append(check_box)
    return result


def create_brightness(
    main_window: QMainWindow, n_channels: int
) -> list[BoxedRangeSlider]:
    result = []
    for k in range(n_channels):
        slider = BoxedRangeSlider(0, 255)
        slider.setMinimumHeight(30)
        slider.slider.valueChanged.connect(main_window.update_brightness)
        result.append(slider)
    return result


def create_label(main_window: QMainWindow) -> ScrollLabel:
    result = ScrollLabel(main_window)
    result.label.setMouseTracking(True)
    return result


def create_zoom(main_window: QMainWindow) -> QSlider:
    result = QSlider(QtCore.Qt.Horizontal)
    result.setMinimum(100)
    result.setMaximum(800)
    result.valueChanged.connect(lambda: main_window.update_zoom())
    return result


def create_center_size_slider(main_window: QMainWindow) -> QSlider:
    result = QSlider(QtCore.Qt.Horizontal)
    result.setMinimum(1)
    result.setMaximum(10)
    result.setValue(5)
    result.valueChanged.connect(lambda: main_window.update_center_size())
    return result