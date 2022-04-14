import sys
import os
import functools as ft
from typing import Literal
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, QWidget, QPushButton, QGridLayout, QToolBar, QCheckBox, QFileDialog, QSlider, QMessageBox, QLineEdit
from PyQt5.QtGui import QIntValidator
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
import traceback
import datetime

import numpy as np
import pandas as pd
from center_of_blob import analyze
from center_of_blob.main_image import ScrollLabel
from center_of_blob.channels import Channels, N_CHANNELS
from center_of_blob.centers import Centers, Center
from center_of_blob.popups import error_msg, about_dialog
from center_of_blob.boxed_range_slider import BoxedRangeSlider
from center_of_blob.region import Region


# TODO: Why do we have to use lambda with the .connect calls below when using this?
def require_image(func):
    def wrapper(self, *args, **kwargs):
        if not self.has_img:
            error_msg("Must load image first.")
            return
        return func(self, *args, **kwargs)
    return wrapper


class QLabelDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.state = 'none'
        self.origin: tuple[float, float] | None = None
        self.channels = Channels()
        self.filename = None
        self.centers = Centers()
        self.button_states = {}
        self.has_img = False
        self.colors = {0: False, 1: False, 2: False}
        self.current_region = None
        self.regions = []
        self.show_centers = True
        self.center_colors = "normal"
        self.enable_tooltip = True

        self.img_path_button = QPushButton("Select Image File")
        self.img_path_button.clicked.connect(self.get_img_file)

        self.centers_path_button = QPushButton("Select Centers File")
        self.centers_path_button.clicked.connect(lambda: self.get_centers_file())

        self.set_origin_button = QPushButton('Start setting origin', self)
        self.set_origin_button.setToolTip('Click this button and then click on the desired origin')
        self.set_origin_button.resize(150, 50)
        self.set_origin_button.clicked.connect(lambda: self.activate_set_origin())
        self.button_states['setting_origin'] = self.set_origin_button

        locate_blobs = QPushButton('Locate blobs', self)
        locate_blobs.setToolTip('Click this button to locate blobs')
        locate_blobs.resize(150, 50)
        locate_blobs.clicked.connect(lambda: self.locate_blobs())

        self.modify_centers = QPushButton('Start modifying centers', self)
        self.modify_centers.resize(150, 50)
        self.modify_centers.clicked.connect(lambda: self.activate_modify_centers())
        self.button_states['modifying_centers'] = self.modify_centers

        self.draw_region = QPushButton('Start drawing region', self)
        self.draw_region.resize(150, 50)
        self.draw_region.clicked.connect(lambda: self.activate_drawing_region())
        self.button_states['drawing_region'] = self.draw_region

        # self.zoom_in = QPushButton('Zoom in', self)
        # self.zoom_in.resize(150, 50)
        # self.zoom_in.clicked.connect(lambda: self.zoom('in'))
        #
        # self.zoom_out = QPushButton('Zoom out', self)
        # self.zoom_out.resize(150, 50)
        # self.zoom_out.clicked.connect(lambda: self.zoom('out'))

        write_csv = QPushButton('Write CSV', self)
        write_csv.resize(150, 50)
        write_csv.clicked.connect(lambda: self.write_csv())

        self.mouse_colors = []
        for k in range(1, N_CHANNELS):
            check_box = QCheckBox(f'Color Channel {k}')
            check_box.setChecked(False)
            check_box.stateChanged.connect(lambda: self.update_mouse_colors())
            self.mouse_colors.append(check_box)

        self.show_channels = []
        for k in range(N_CHANNELS):
            check_box = QCheckBox(f'Channel {k}')
            check_box.setChecked(k == 0)
            check_box.stateChanged.connect(lambda: self.update_channels())
            self.show_channels.append(check_box)

        self.brightness_low = []
        self.brightness_high = []
        self.brightness = []
        for k in range(N_CHANNELS):
            slider = BoxedRangeSlider(0, 255)
            slider.setMinimumHeight(30)
            # slider.sliderMoved.connect(lambda _, _2, k=k: self.update_brightness_boxes(k))
            slider.slider.valueChanged.connect(self.update_brightness)
            self.brightness.append(slider)

        self.label = ScrollLabel(self)
        self.label.label.setMouseTracking(True)
        # self.label.viewport().installEventFilter(self)

        self.zoom = QSlider(QtCore.Qt.Horizontal)
        self.zoom.setMinimum(100)
        self.zoom.setMaximum(800)
        self.zoom.valueChanged.connect(lambda: self.update_zoom())

        main = QWidget(self)
        self.setCentralWidget(main)
        layout = QGridLayout()
        layout.addWidget(self.img_path_button, 0, 0)
        layout.addWidget(self.centers_path_button, 0, 1)
        layout.addWidget(write_csv, 0, 2)
        layout.addWidget(self.set_origin_button, 1, 0)
        layout.addWidget(self.modify_centers, 1, 1)
        layout.addWidget(self.draw_region, 1, 2)
        # layout.addWidget(self.zoom_in, 2, 0)
        # layout.addWidget(self.zoom_out, 2, 1)
        layout.addWidget(locate_blobs, 2, 2)
        for k in range(N_CHANNELS):
            layout.addWidget(self.show_channels[k], k, 3)
            layout.addWidget(self.brightness[k], k, 6)
        for k, checkbox in enumerate(self.mouse_colors):
            layout.addWidget(checkbox, 3, k)
        layout.addWidget(self.zoom, 4, 0, 1, 7)
        layout.addWidget(self.label, 5, 0, 1, 7)

        # layout.setColumnStretch(6, 1)
        # layout.setRowStretch(4, 1)

        main.setLayout(layout)

        self.setWindowTitle('QLabel Example')
        self.label.label.installEventFilter(self)

        self.setGeometry(100, 100, 500, 400)

        menubar = self.menuBar()
        help = menubar.addMenu("Help")
        show_about = QAction('About', self)
        show_about.triggered.connect(about_dialog)
        help.addAction(show_about)

    @require_image
    def update_zoom(self):
        self.label.zoom(self.zoom.value() / 100)

    # @require_image
    # def zoom(self, how: Literal['in', 'out']) -> None:
    #     self.label.zoom(how)

    def update_channels(self):
        self.label.invalidate_cache()
        self.label.update_image()

    def update_brightness(self, dummy):
        for channel, slider in enumerate(self.brightness):
            low = slider.low()
            high = slider.high()
            self.channels.set_brightness(channel, low, high)
        if self.has_img:
            self.label.invalidate_cache()
            self.label.update_image()

    def update_mouse_colors(self):
        for k, checkbox in enumerate(self.mouse_colors):
            self.colors[k] = checkbox.isChecked()

    def get_img_file(self):
        self.state = 'none'
        self.origin = None
        self.channels = Channels()
        self.filename = None
        self.centers = Centers()
        self.has_img = False
        self.colors = {0: False, 1: False, 2: False}
        self.current_region = None
        self.regions = []
        self.show_centers = True
        self.center_colors = "normal"

        mypath = os.path.dirname(os.path.realpath(__file__))
        path = QFileDialog.getOpenFileName(
            self,
            'Open Image File',
            mypath,
        )[0]
        try:
            self.channels.load_image(path)
        except Exception as err:
            error_msg(f"Failed to load file\n\n{path}\n\nError message:\n\n{err}")
        else:
            self.has_img = True
            self.filename = path
            self.centers.clear()
            self.label.reset_image()

    def make_regions(self, data):
        data = data[data['kind'] == 'region']
        for name, df in data.groupby('region'):
            points = zip(df['x'], df['y'])
            region = Region()
            for point in points:
                region.add_point(point)
            region.name = name
            self.regions.append(region)

    @require_image
    def get_centers_file(self):
        self.state = 'none'
        self.origin = None
        self.channels = Channels()
        self.filename = None
        self.centers = Centers()
        self.has_img = False
        self.colors = {0: False, 1: False, 2: False}
        self.current_region = None
        self.regions = []
        self.show_centers = True
        self.center_colors = "normal"

        mypath = os.path.dirname(os.path.realpath(__file__))
        path = QFileDialog.getOpenFileName(
            self,
            'Open Centers File',
            mypath,
        )[0]
        try:
            data = pd.read_csv(path)
            values = data[data['kind'] == 'center'].query("distance > 0")
            for _, row in values.iterrows():
                self.centers[row.x, row.y] = Center(row.x, row.y, (row.red, row.green, row.blue), row.region)
            self.make_regions(data)
        except Exception as err:
            error_msg(f"Failed to load file\n\n{path}\n\nError message:\n\n{err}")
            return

        if not self.centers.are_in_img(self.channels[0].shape):
            self.centers.clear()
            error_msg("Centers file has points outside of image bounds. Refusing file.")
            return

        try:
            point = data[data['kind'] == 'origin'].iloc[0]
            self.origin = point['x'], point['y']
        except Exception as err:
            error_msg(f"Failed to find origin in centers file. Error message:\n\n{err}")
            self.centers.clear()
            return

        self.label.update_image()

    @require_image
    def activate_set_origin(self):
        if self.state == 'setting_origin':
            self.state = 'none'
        else:
            self.state = 'setting_origin'
        self.update_state_buttons()

    @require_image
    def activate_modify_centers(self):
        if self.state == 'modifying_centers':
            self.state = 'none'
        else:
            self.state = 'modifying_centers'
        self.update_state_buttons()

    @require_image
    def activate_drawing_region(self):
        if self.state == 'drawing_region':
            self.state = 'none'
        else:
            self.state = 'drawing_region'
            self.current_region = Region()
        self.update_state_buttons()

    def add_region_point(self, source, event):
        x, y = self.mouse_to_pixel(event.pos().x(), event.pos().y())
        self.current_region.add_point((x, y))
        self.label.update_image()

    def classify_center_by_regions(self, point, center):
        buffer = []
        for region in self.regions:
            if region.contains(point):
                buffer.append(region)
        if len(buffer) == 0:
            center.region = ''
            return

        region = buffer[0]
        names = sorted(set(e.name for e in buffer))
        if len(names) > 1:
            msg = (
                'Center belongs to multiple regions with different names:\n'
            )
            for name in names:
                msg += f'  {name}\n'
            msg += f'Classifying as {region.name}'
            error_msg(msg)
        center.region = region.name

    def classify_centers_by_regions(self):
        if len(self.centers) == 0:
            return
        for point, center in self.centers.items():
            self.classify_center_by_regions(point, center)

    @require_image
    def stop_drawing_region(self):
        self.current_region.close()
        if len(self.current_region) > 0:
            name, done1 = QtWidgets.QInputDialog.getText(self, 'Name Region', 'Enter region name:')
            self.current_region.name = name
            self.regions.append(self.current_region)
            self.classify_centers_by_regions()

            self.label.update_image()
        self.current_region = None

    @require_image
    def update_state_buttons(self):
        for name, button in self.button_states.items():
            label_text = name.replace('_', ' ')
            if self.state == name:
                button.setText(f'Stop {label_text}')
            else:
                button.setText(f'Start {label_text}')
        if self.state != 'drawing_region' and self.current_region is not None:
            self.stop_drawing_region()

    @require_image
    def add_center(self, source, event):
        new_color = self.active_color()
        if new_color == (0, 0, 0):
            return
        x, y = self.mouse_to_pixel(event.pos().x(), event.pos().y())
        closest = self.centers.closest((x, y), radius=10)

        if closest is None:
            current_color = (0, 0, 0)
        else:
            current_color = self.centers[closest].color
            x, y = closest
        color = self.union_colors(current_color, new_color)
        self.centers[x, y] = Center(x, y, color, '')
        self.classify_center_by_regions((x, y), self.centers[x, y])
        self.label.update_image()

    def active_color(self):
        channels = [k for k, v in self.colors.items() if v]
        result = tuple(255 if k in channels else 0 for k in range(3))
        return result

    def union_colors(self, color1, color2):
        return tuple(max(e1, e2) for e1, e2 in zip(color1, color2))

    def subtract_colors(self, color1, color2):
        return tuple(max(0, e1 - e2) for e1, e2 in zip(color1, color2))

    @require_image
    def remove_center(self, source, event):
        x, y = self.mouse_to_pixel(event.pos().x(), event.pos().y())
        closest = self.centers.closest((x, y), radius=30)
        if closest is not None:
            del self.centers[closest]
            self.label.update_image()

    @require_image
    def remove_region(self, source, event):
        x, y = self.mouse_to_pixel(event.pos().x(), event.pos().y())
        for k, region in enumerate(self.regions):
            if region.contains_point((x, y), radius=30):
                self.regions.pop(k)
                self.classify_centers_by_regions()
                self.label.update_image()
                return

    def update_mouse_tooltip(self, source, event):
        if not self.has_img:
            return
        if not self.enable_tooltip:
            self.label.setToolTip('')
            return
        point = self.mouse_to_pixel(event.pos().x(), event.pos().y())

        buffer = []
        for region in self.regions:
            if region.contains(point):
                buffer.append(region.name)
        self.label.setToolTip(', '.join(buffer))
        self.label.setToolTipDuration(1500)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if self.state == 'setting_origin' and event.button() == QtCore.Qt.LeftButton:
                self.set_origin(source, event)
            elif self.state == 'modifying_centers':
                if event.button() == QtCore.Qt.LeftButton:
                    self.add_center(source, event)
                elif event.button() == QtCore.Qt.RightButton:
                    self.remove_center(source, event)
            elif self.state == 'drawing_region':
                if event.button() == QtCore.Qt.LeftButton:
                    self.add_region_point(source, event)
            elif event.button() == QtCore.Qt.RightButton:
                self.remove_region(source, event)
        if event.type() == QtCore.QEvent.MouseMove and self.enable_tooltip:
            self.update_mouse_tooltip(source, event)

        if event.type() == QtCore.QEvent.Wheel:
            modifiers = QApplication.keyboardModifiers()
            if bool(modifiers == QtCore.Qt.ControlModifier):
                self.zoom.setValue(self.zoom.value() + int(event.angleDelta().y() / 5))
                event.ignore()
        return super().eventFilter(source, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_R or event.key() == Qt.Key_1:
            self.mouse_colors[0].setChecked(not self.mouse_colors[0].isChecked())
        elif event.key() == Qt.Key_G or event.key() == Qt.Key_2:
            self.mouse_colors[1].setChecked(not self.mouse_colors[1].isChecked())
        elif event.key() == Qt.Key_B or event.key() == Qt.Key_3:
            self.mouse_colors[2].setChecked(not self.mouse_colors[2].isChecked())
        elif event.key() == Qt.Key_A:
            self.show_channels[0].setChecked(not self.show_channels[0].isChecked())
        elif event.key() == Qt.Key_S:
            self.show_channels[1].setChecked(not self.show_channels[1].isChecked())
        elif event.key() == Qt.Key_D:
            self.show_channels[2].setChecked(not self.show_channels[2].isChecked())
        elif event.key() == Qt.Key_F:
            self.show_channels[3].setChecked(not self.show_channels[3].isChecked())
        elif event.key() == Qt.Key_Space:
            self.show_centers = not self.show_centers
            self.label.update_image()
        elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            if self.center_colors == "normal":
                self.center_colors = "black"
            else:
                self.center_colors = "normal"
            self.label.update_image()
        elif event.key() == Qt.Key_T:
            self.enable_tooltip = not self.enable_tooltip
        event.accept()

    @require_image
    def set_origin(self, source, event):
        x, y = self.mouse_to_pixel(event.pos().x(), event.pos().y())
        self.origin = (x, y)
        self.state = 'none'
        self.update_state_buttons()
        self.label.update_image()

    @require_image
    def mouse_to_pixel(self, x, y):
        # Prefer numpy C-style coordinates: x=row, y=column
        x, y = y, x
        x_pct = x / self.label.label.width()
        y_pct = y / self.label.label.height()
        result = int(x_pct * self.channels.width), int(y_pct * self.channels.height)
        return result

    @require_image
    def locate_blobs(self):
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        for channel, color in zip(self.channels[1:], colors):
            centers = analyze.identify_centers(
                channel,
                sigma=2.0,
                gaussian_cutoff=20,
                open_structure=np.ones((5, 5)),
                open_iterations=1,
            )
            for center in centers:
                self.centers[center] = Center(*center, color, '')
        self.label.update_image()

    # TODO: Type Overload
    @require_image
    def visible_channels(self, dtype=int) -> list[int | str]:
        visible_channels = [k for k, checkbox in enumerate(self.show_channels) if checkbox.isChecked()]
        if dtype is int:
            return visible_channels
        else:
            mapper = self.channels.mapper
            return {k: mapper[v] for k, v in visible_channels.items()}

    @require_image
    def write_csv(self):
        if self.origin is None:
            error_msg("Must set origin to write CSV file.")
            return
        if len(self.centers) == 0:
            error_msg("Must set at least one center to write CSV file.")
            return

        x0, y0 = self.origin
        data = []
        data.append(['origin', x0, y0, 0, 0, 0, 0])
        for (x, y), center in self.centers.items():
            distance = np.sqrt((x - x0) * (x - x0) + (y - y0) * (y - y0))
            data.append(['center', x, y, distance, *center.color, center.region])
        for region in self.regions:
            for point in region.points:
                data.append(['region', *point, -1, 255, 69, 0, region.name])
        suggested_filename = f"{os.path.splitext(self.filename)[0]}.csv"
        name = QFileDialog.getSaveFileName(self, 'Save File', suggested_filename)[0]

        pd.DataFrame(
            data,
            columns=['kind', 'x', 'y', 'distance', 'red', 'green', 'blue', 'region']
        ).to_csv(name, index=False)


def except_hook(cls, exception, tb):
    timestamp = datetime.datetime.now()
    stacktrace = traceback.format_tb(tb)
    msg = f'Error: {cls} -- {exception}\nStacktrace\n'
    for line in stacktrace:
        msg += f'{line}\n'
    filename = f'cob_error_{timestamp}.log'
    with open(filename, 'w') as f:
        f.write(msg)
    error_msg(f'Unexpected exception occured. The file \n\n{filename}\n\n was created with the following log\n\n{msg}\n')


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    main = QLabelDemo()
    main.show()
    sys.exit(app.exec_())

