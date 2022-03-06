import sys
import os
import functools as ft
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QCheckBox, QFileDialog, QSlider

from PyQt5 import QtCore

import numpy as np
import pandas as pd
from center_of_blob import analyze
from center_of_blob.main_image import ScrollLabel
from center_of_blob.channels import Channels, N_CHANNELS
from center_of_blob.centers import Centers


class QLabelDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.state = 'none'
        self.origin: tuple[float, float] | None = None
        self.channels = None
        self.filename = None

        self.centers = Centers()
        self.button_states = {}

        self.img_path_button = QPushButton("Select Image File")
        self.img_path_button.clicked.connect(self.get_img_file)

        self.centers_path_button = QPushButton("Select Centers File")
        self.centers_path_button.clicked.connect(self.get_centers_file)

        self.set_origin = QPushButton('Start setting origin', self)
        self.set_origin.setToolTip('Click this button and then click on the desired origin')
        self.set_origin.resize(150, 50)
        self.set_origin.clicked.connect(self.activate_set_origin)
        self.button_states['setting_origin'] = self.set_origin

        locate_blobs = QPushButton('Locate blobs', self)
        locate_blobs.setToolTip('Click this button to locate blobs')
        locate_blobs.resize(150, 50)
        locate_blobs.clicked.connect(self.locate_blobs)

        self.modify_centers = QPushButton('Start modifying centers', self)
        self.modify_centers.resize(150, 50)
        self.modify_centers.clicked.connect(self.activate_modify_centers)
        self.button_states['modifying_centers'] = self.modify_centers

        self.zoom_in = QPushButton('Zoom in', self)
        self.zoom_in.resize(150, 50)
        self.zoom_in.clicked.connect(lambda: self.label.zoom('in'))

        self.zoom_out = QPushButton('Zoom out', self)
        self.zoom_out.resize(150, 50)
        self.zoom_out.clicked.connect(lambda: self.label.zoom('out'))

        write_csv = QPushButton('Write CSV', self)
        write_csv.resize(150, 50)
        write_csv.clicked.connect(self.write_csv)

        self.show_channels = []
        for k in range(N_CHANNELS):
            check_box = QCheckBox(f'Channel {k}')
            check_box.setChecked(k == 0)
            check_box.stateChanged.connect(lambda: self.label.update_image())
            self.show_channels.append(check_box)

        self.brightness_mul = []
        for k in range(N_CHANNELS):
            slider = QSlider(QtCore.Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(5000)
            slider.setValue(1000)
            updater = ft.partial(self.update_brightness_mul, k)
            slider.valueChanged.connect(updater)
            self.brightness_mul.append(slider)

        self.label = ScrollLabel(self)

        layout = QGridLayout()
        layout.addWidget(self.img_path_button, 0, 0)
        layout.addWidget(self.centers_path_button, 0, 1)
        layout.addWidget(write_csv, 0, 2)
        layout.addWidget(self.set_origin, 1, 0)
        layout.addWidget(self.modify_centers, 1, 1)
        layout.addWidget(locate_blobs, 1, 2)
        layout.addWidget(self.zoom_in, 2, 0)
        layout.addWidget(self.zoom_out, 2, 1)
        for k in range(N_CHANNELS):
            layout.addWidget(self.show_channels[k], k, 3)
            layout.addWidget(self.brightness_mul[k], k, 4)
        layout.addWidget(self.label, 4, 0, 1, 5)
        self.setLayout(layout)

        self.setWindowTitle('QLabel Example')
        self.label.label.installEventFilter(self)

        self.setGeometry(100, 100, 500, 400)

    def update_brightness_mul(self, channel):
        value = self.brightness_mul[channel].value() / 1000
        self.channels.set_brightness_mul(channel, value)
        self.label.update_image()

    def get_img_file(self):
        mypath = os.path.dirname(os.path.realpath(__file__))
        path = QFileDialog.getOpenFileName(
            self,
            'Open Image File',
            mypath,
        )[0]
        self.filename = path
        self.channels = Channels(path)
        self.centers.clear()
        self.label.reset_image()

    def get_centers_file(self):
        # TODO: Make sure centers is empty?
        mypath = os.path.dirname(os.path.realpath(__file__))
        path = QFileDialog.getOpenFileName(
            self,
            'Open Centers File',
            mypath,
        )[0]
        data = pd.read_csv(path).set_index(['x', 'y'])
        self.origin = data[data["distance"].lt(1e-5)].index[0]
        self.centers = Centers(
            data
            .query("distance > 0")
            .drop(columns='distance')
            .apply(tuple, axis=1)
            .to_dict()
        )
        self.label.update_image()

    def activate_set_origin(self):
        if self.state == 'setting_origin':
            self.state = 'none'
        else:
            self.state = 'setting_origin'
        self.update_state_buttons()

    def activate_modify_centers(self):
        if self.state == 'modifying_centers':
            self.state = 'none'
        else:
            self.state = 'modifying_centers'
        self.update_state_buttons()

    def update_state_buttons(self):
        for name, button in self.button_states.items():
            label_text = name.replace('_', ' ')
            if self.state == name:
                button.setText(f'Stop {label_text}')
            else:
                button.setText(f'Start {label_text}')

    def add_center(self, source, event):
        x, y = self.mouse_to_pixel(event.pos().x(), event.pos().y())
        closest = self.centers.closest((x, y), radius=10)
        if closest is None:
            self.centers[x, y] = self.channels.color(self.visible_channels())
            self.label.update_image()

    def remove_center(self, source, event):
        x, y = self.mouse_to_pixel(event.pos().x(), event.pos().y())
        closest = self.centers.closest((x, y), radius=30)
        if closest is not None:
            del self.centers[closest]
            self.label.update_image()

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if self.state == 'setting_origin' and event.button() == QtCore.Qt.LeftButton:
                x, y = self.mouse_to_pixel(event.pos().x(), event.pos().y())
                self.origin = (x, y)
                self.state = 'none'
                self.update_state_buttons()
                self.label.update_image()
            elif self.state == 'modifying_centers':
                if event.button() == QtCore.Qt.LeftButton:
                    self.add_center(source, event)
                elif event.button() == QtCore.Qt.RightButton:
                    self.remove_center(source, event)

        return super().eventFilter(source, event)

    def get_label_pos(self, pos) -> tuple[int, int]:
        local_pos = self.label.mapFromParent(pos)
        # contentsRect = QtCore.QRectF(self.label.contentsRect())
        # local_pos -= contentsRect.topLeft()
        x, y = int(local_pos.x()), int(local_pos.y())
        return x, y

    def mouse_to_pixel(self, x, y):
        # Prefer numpy C-style coordinates: x=row, y=column
        x, y = y, x
        x_pct = x / self.label.label.width()
        y_pct = y / self.label.label.height()
        result_x = int(x_pct * self.channels.width)
        result_y = int(y_pct * self.channels.height)
        return result_x, result_y

    def locate_blobs(self):
        self.centers = analyze.identify_centers(self.channels.base.arr)
        self.label.update_image()

    # TODO: Overload
    def visible_channels(self, dtype=int) -> list[int | str]:
        visible_channels = [k for k, checkbox in enumerate(self.show_channels) if checkbox.isChecked()]
        if dtype is int:
            return visible_channels
        else:
            mapper = self.channels.mapper
            return {k: mapper[v] for k, v in visible_channels.items()}

    def write_csv(self):
        if self.origin is None:
            return
        if len(self.centers) == 0:
            return

        x0, y0 = self.origin
        data = []
        data.append([x0, y0, 0, 0, 0, 0])
        for (x, y), color in self.centers.items():
            distance = np.sqrt((x - x0) * (x - x0) + (y - y0) * (y - y0))
            data.append([x, y, distance, *color])
        suggested_filename = f"{os.path.splitext(self.filename)[0]}.csv"
        name = QFileDialog.getSaveFileName(self, 'Save File', suggested_filename)[0]

        pd.DataFrame(
            data,
            columns=['x', 'y', 'distance', 'red', 'green', 'blue']
        ).to_csv(name, index=False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = QLabelDemo()
    main.show()
    sys.exit(app.exec_())
