import sys
from PyQt5.QtWidgets import QApplication,QLabel,QWidget, QPushButton, QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from PIL import Image
import numpy as np
import pandas as pd
import analyze
from main_image import ScrollLabel


class QLabelDemo(QWidget):
    def __init__(self):
        self.state = 'none'
        self.origin: tuple[float, float] | None = None
        self.filename = "second.tif"
        self.image = Image.open(self.filename)
        self.arr = np.asarray(self.image)
        self.centers = []
        self.button_states = {}

        print('Format:', self.image.format)
        print('Size:', self.image.size)
        print('Mode:', self.image.mode)

        super().__init__()
        self.initUI()
        self.setGeometry(100, 100, 500, 400)

    def initUI(self):
        self.label = ScrollLabel(self.filename)

        self.set_origin = QPushButton('Start setting origin', self)
        self.set_origin.setToolTip('Click this button and then click on the desired origin')
        self.set_origin.resize(150, 50)
        self.set_origin.clicked.connect(self.activate_set_origin)
        self.button_states['setting_origin'] = self.set_origin

        locate_blobs = QPushButton('Locate blobs', self)
        locate_blobs.setToolTip('Click this button to locate blobs')
        locate_blobs.resize(150, 50)
        locate_blobs.clicked.connect(self.locate_blobs)

        self.remove_centers = QPushButton('Start removing centers', self)
        self.remove_centers.resize(150, 50)
        self.remove_centers.clicked.connect(self.activate_remove_centers)
        self.button_states['removing_centers'] = self.remove_centers

        self.add_centers = QPushButton('Start adding centers', self)
        self.add_centers.resize(150, 50)
        self.add_centers.clicked.connect(self.activate_add_centers)
        self.button_states['adding_centers'] = self.add_centers

        self.zoom_in = QPushButton('Zoom in', self)
        self.zoom_in.resize(150, 50)
        self.zoom_in.clicked.connect(lambda: self.label.zoom('in'))

        self.zoom_out = QPushButton('Zoom out', self)
        self.zoom_out.resize(150, 50)
        self.zoom_out.clicked.connect(lambda: self.label.zoom('out'))

        write_csv = QPushButton('Write CSV', self)
        write_csv.resize(150, 50)
        write_csv.clicked.connect(self.write_csv)

        layout = QGridLayout()
        layout.addWidget(self.set_origin, 0, 0)
        layout.addWidget(locate_blobs, 0, 1)
        layout.addWidget(self.remove_centers, 1, 0)
        layout.addWidget(self.add_centers, 1, 1)
        layout.addWidget(write_csv, 2, 0)
        layout.addWidget(self.zoom_in, 3, 0)
        layout.addWidget(self.zoom_out, 3, 1)
        layout.addWidget(self.label, 4, 0, 1, 2)
        self.setLayout(layout)

        self.setWindowTitle('QLabel Example')
        # self.installEventFilter(self)
        self.label.label.installEventFilter(self)
        # self.label.setMouseTracking(True)

    def linkHovered(self):
        print('Link hovered')

    def linkClicked(self):
        print('Link clicked')

    def activate_set_origin(self):
        if self.state == 'setting_origin':
            self.state = 'none'
        else:
            self.state = 'setting_origin'
        self.update_state_buttons()

    def activate_add_centers(self):
        if self.state == 'adding_centers':
            self.state = 'none'
        else:
            self.state = 'adding_centers'
        self.update_state_buttons()

    def activate_remove_centers(self):
        if self.state == 'removing_centers':
            self.state = 'none'
        else:
            self.state = 'removing_centers'
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
        self.centers.append((x, y))
        self.update_pixmap()

    def remove_center(self, source, event):
        x, y = self.mouse_to_pixel(event.pos().x(), event.pos().y())
        closest, shortest_distance = None, None
        for idx, (x2, y2) in enumerate(self.centers):
            distance = (x - x2) * (x - x2) + (y - y2) * (y - y2)
            if closest is None or distance < shortest_distance:
                closest = idx
                shortest_distance = distance
        if shortest_distance is None or shortest_distance > 900:
            print(shortest_distance)
            return
        del self.centers[closest]
        self.update_pixmap()

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.MouseButtonPress and event.button() == QtCore.Qt.LeftButton:
            if self.state == 'setting_origin':
                x, y = self.mouse_to_pixel(event.pos().x(), event.pos().y())
                self.origin = (x, y)
                self.state = 'none'
                self.update_state_buttons()
                self.update_pixmap()
            elif self.state == 'removing_centers':
                self.remove_center(source, event)
            elif self.state == 'adding_centers':
                self.add_center(source, event)

        # if event.type() == QtCore.QEvent.MouseMove:
        #     x, y = event.pos().x(), event.pos().y()
        #     rect = self.label.rect()
        #     label_w, label_h = rect.width(), rect.height()
        #     x_pct = x / label_w
        #     y_pct = y / label_h
        #     x = int(x_pct * self.image.size[0])
        #     y = int(y_pct * self.image.size[1])
        #     try:
        #         color = self.df.loc[x, y].tolist()
        #     except KeyError:
        #         color = 'Out of bounds'
        #     print((x, y), color)

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
        result_x = int(x_pct * self.image.width)
        result_y = int(y_pct * self.image.height)
        return result_x, result_y

    def locate_blobs(self):
        self.centers = analyze.identify_centers(self.arr)
        self.update_pixmap()

    def update_pixmap(self):
        new_data = analyze.highlight_points(self.arr, self.centers)
        if self.origin is not None:
            analyze.highlight_point(new_data, self.origin, color=(255, 255, 0))

        height, width, channel = new_data.shape
        bytes_per_line = 3 * width
        new_image = QtGui.QImage(new_data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
        new_pixmap = QtGui.QPixmap.fromImage(new_image)

        # set pixmap onto the label widget
        self.label._update_image(new_pixmap)
        self.label.show()

    def write_csv(self):
        if self.origin is None:
            return
        if len(self.centers) == 0:
            return

        x0, y0 = self.origin
        data = []
        data.append([0, x0, y0, 0])
        for k, (x, y) in enumerate(self.centers, 1):
            distance = np.sqrt((x - x0) * (x - x0) + (y - y0) * (y - y0))
            data.append([k, x, y, distance])
        pd.DataFrame(data, columns=['point', 'x', 'y', 'distance']).to_csv('../output.csv', index=False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = QLabelDemo()
    main.show()
    sys.exit(app.exec_())
