from __future__ import annotations

import datetime
import os
import sys
import traceback
from pathlib import Path

import numpy as np
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QGridLayout,
    QMainWindow,
    QPushButton,
    QWidget,
)

from center_of_blob import widgets
from center_of_blob.centers import Center, Centers
from center_of_blob.channels import N_CHANNELS, Channels
from center_of_blob.popups import (
    CsvNameDialog,
    ImageNameDialog,
    about_dialog,
    error_msg,
    info_dialog,
    shortcuts_dialog,
)
from center_of_blob.region import Region


# TODO: Why do we have to use lambda with the .connect calls below when using this?
def require_image(func):
    def wrapper(self, *args, **kwargs):
        if not self.has_img:
            error_msg("Must load image first.")
            return
        return func(self, *args, **kwargs)

    return wrapper


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.state = "none"
        self.origin: tuple[float, float] | None = None
        self.channels = Channels()
        self.filename: str | None = None
        self.centers = Centers()
        self.button_states: dict[str, QPushButton] = {}
        self.has_img = False
        self.colors = {0: False, 1: False, 2: False}
        self.current_region: Region | None = None
        self.regions: list[Region] = []
        self.show_centers = [1, 2, 3]
        self.center_colors = "normal"
        self.enable_tooltip = True

        self.img_path_button = widgets.create_img_path_button(self)
        self.centers_path_button = widgets.create_centers_path_button(self)
        self.set_origin_button = widgets.create_set_origin_button(self)
        self.modify_centers = widgets.create_modify_centers(self)
        self.draw_region = widgets.create_draw_region(self)
        self.write_csv_button = widgets.create_write_csv_button(self)
        self.mouse_colors = widgets.create_mouse_colors(self, N_CHANNELS)
        self.show_channels = widgets.create_show_channels(self, N_CHANNELS)
        self.show_center_checkboxes = widgets.create_show_center_checkboxes(
            self, N_CHANNELS
        )
        self.brightness = widgets.create_brightness(self, N_CHANNELS)
        self.label = widgets.create_label(self)
        self.zoom = widgets.create_zoom(self)
        self.center_size_slider = widgets.create_center_size_slider(self)

        self.button_states["setting_origin"] = self.set_origin_button
        self.button_states["modifying_centers"] = self.modify_centers
        self.button_states["drawing_region"] = self.draw_region

        main = QWidget(self)
        self.setCentralWidget(main)
        layout = QGridLayout()
        layout.addWidget(self.img_path_button, 0, 0)
        layout.addWidget(self.centers_path_button, 0, 1)
        layout.addWidget(self.write_csv_button, 0, 2)
        layout.addWidget(self.set_origin_button, 1, 0)
        layout.addWidget(self.modify_centers, 1, 1)
        layout.addWidget(self.draw_region, 1, 2)
        for k in range(N_CHANNELS):
            layout.addWidget(self.show_channels[k], k, 3)
            if k > 0:
                layout.addWidget(self.show_center_checkboxes[k], k, 4)
            layout.addWidget(self.brightness[k], k, 5)
        for k, checkbox in enumerate(self.mouse_colors):
            layout.addWidget(checkbox, 3, k)
        layout.addWidget(self.zoom, 4, 0, 1, 6)
        layout.addWidget(self.center_size_slider, 5, 0, 1, 6)
        layout.addWidget(self.label, 6, 0, 1, 6)

        main.setLayout(layout)

        self.setWindowTitle("Center of Blob - No File Loaded")
        self.label.label.installEventFilter(self)

        self.setGeometry(100, 100, 500, 400)

        menubar = self.menuBar()
        help = menubar.addMenu("Help")

        show_info = QAction("Info", self)
        show_info.setObjectName("action_show_info")
        show_info.triggered.connect(lambda: info_dialog(self))

        show_shortcuts = QAction("Shortcuts", self)
        show_shortcuts.setObjectName("action_show_shortcuts")
        show_shortcuts.triggered.connect(lambda: shortcuts_dialog(self))

        show_about = QAction("About", self)
        show_about.setObjectName("action_show_about")
        show_about.triggered.connect(about_dialog)

        help.addAction(show_info)
        help.addAction(show_shortcuts)
        help.addAction(show_about)

        self.showMaximized()

        img_path = os.environ.get("COB_IMAGE_PATH")
        if img_path is not None:
            self.get_img_file(img_path)

    @require_image
    def update_zoom(self) -> None:
        self.label.zoom(self.zoom.value() / 100)

    @require_image
    def update_center_size(self) -> None:
        self.label.invalidate_cache()
        self.label.update_image()

    def update_channels(self) -> None:
        self.label.invalidate_cache()
        self.label.update_image()

    def update_centers(self) -> None:
        self.show_centers = []
        for k in range(1, N_CHANNELS):
            if self.show_center_checkboxes[k].isChecked():
                self.show_centers.append(k)
        self.label.invalidate_cache()
        self.label.update_image()

    def update_brightness(self, dummy) -> None:
        for channel, slider in enumerate(self.brightness):
            low = slider.low()
            high = slider.high()
            self.channels.set_brightness(channel, low, high)
        if self.has_img:
            self.label.invalidate_cache()
            self.label.update_image()

    def update_mouse_colors(self) -> None:
        for k, checkbox in enumerate(self.mouse_colors):
            self.colors[k] = checkbox.isChecked()

    def get_img_file(self, path: str | Path | None = None) -> None:
        if isinstance(path, str):
            path = Path(path)
        mypath = str(Path(__file__).resolve())
        print(type(path), path)
        if path is None:
            path = Path(ImageNameDialog.getOpenFileName(self, mypath)).resolve()
        try:
            # TODO: load_image resets channel state.. bad design
            disable_channel_0 = self.channels.load_image(str(path))
        except Exception as err:
            error_msg(f"Failed to load file\n\n{path}\n\nError message:\n\n{err}")
        else:
            self.state = "none"
            self.center_colors = "normal"
            self.show_centers = [1, 2, 3]
            self.has_img = True
            self.filename = str(path)
            self.setWindowTitle(f"Center of Blob - {path.parts[-1]}")
            self.centers.clear()
            self.origin = None
            self.label.reset_image()
            if disable_channel_0:
                self.show_channels[0].setChecked(False)
                self.show_channels[0].setDisabled(True)
                self.brightness[0].setDisabled(True)
            else:
                self.show_channels[0].setDisabled(False)
                self.brightness[0].setDisabled(False)
            self.label._cache = None
            self.current_region = None
            self.regions = []
            self.colors = {0: False, 1: False, 2: False}
            self.label.update_image()

    def make_regions(self, data) -> None:
        data = data[data["kind"] == "region"]
        for name, df in data.groupby("region"):
            points = zip(df["x"], df["y"])
            region = Region()
            for point in points:
                region.add_point(point)
            region.name = name
            self.regions.append(region)

    @require_image
    def get_centers_file(self) -> None:
        mypath = os.path.dirname(os.path.realpath(__file__))
        from center_of_blob.popups import CentersFileDialog

        path = CentersFileDialog.getOpenFileName(self, mypath)
        try:
            data = pd.read_csv(path)
            values = data[data["kind"] == "center"].query("distance > 0")
            new_centers = Centers()
            for _, row in values.iterrows():
                new_centers[row.x, row.y] = Center(
                    row.x, row.y, (row.red, row.green, row.blue), row.region
                )
            self.regions = []
            self.current_region = None
            self.make_regions(data)
        except Exception as err:
            error_msg(f"Failed to load file\n\n{path}\n\nError message:\n\n{err}")
            return

        self.origin = None
        self.centers = new_centers
        self.colors = {0: False, 1: False, 2: False}
        self.show_centers = [1, 2, 3]
        self.center_colors = "normal"

        if not self.centers.are_in_img(self.channels[1].shape):
            self.centers.clear()
            error_msg("Centers file has points outside of image bounds. Refusing file.")
            return

        try:
            point = data[data["kind"] == "origin"].iloc[0]
            self.origin = point["x"], point["y"]
        except Exception as err:
            error_msg(f"Failed to find origin in centers file. Error message:\n\n{err}")
            self.centers.clear()
            return

        self.label.update_image()

    @require_image
    def activate_set_origin(self) -> None:
        if self.state == "setting_origin":
            self.state = "none"
        else:
            self.state = "setting_origin"
        self.update_state_buttons()

    @require_image
    def activate_modify_centers(self) -> None:
        if self.state == "modifying_centers":
            self.state = "none"
        else:
            self.state = "modifying_centers"
        self.update_state_buttons()

    @require_image
    def activate_drawing_region(self) -> None:
        if self.state == "drawing_region":
            self.state = "none"
        else:
            self.state = "drawing_region"
            self.current_region = Region()
        self.update_state_buttons()

    def add_region_point(self, source, event) -> None:
        assert self.current_region is not None
        x, y = self.mouse_to_pixel(event.pos().x(), event.pos().y())
        if not self.channels.pixel_in_image((x, y)):
            return
        self.current_region.add_point((x, y))
        self.label.update_image()

    def classify_center_by_regions(self, point, center) -> None:
        buffer = []
        for region in self.regions:
            if region.contains(point):
                buffer.append(region)
        if len(buffer) == 0:
            center.region = ""
            return

        region = buffer[0]
        names = sorted({e.name for e in buffer})
        if len(names) > 1:
            msg = "Center belongs to multiple regions with different names:\n"
            for name in names:
                msg += f"  {name}\n"
            msg += f"Classifying as {region.name}"
            error_msg(msg)
        center.region = region.name

    def classify_centers_by_regions(self) -> None:
        if len(self.centers) == 0:
            return
        for point, center in self.centers.items():
            self.classify_center_by_regions(point, center)

    @require_image
    def stop_drawing_region(self) -> None:
        assert self.current_region is not None
        self.current_region.close()
        if len(self.current_region) > 0:
            name, done1 = QtWidgets.QInputDialog.getText(
                self, "Name Region", "Enter region name:"
            )
            self.current_region.name = name
            self.regions.append(self.current_region)
            self.classify_centers_by_regions()

            self.label.update_image()
        self.current_region = None

    @require_image
    def update_state_buttons(self) -> None:
        for name, button in self.button_states.items():
            label_text = name.replace("_", " ")
            if self.state == name:
                button.setText(f"Stop {label_text}")
            else:
                button.setText(f"Start {label_text}")
        if self.state != "drawing_region" and self.current_region is not None:
            self.stop_drawing_region()

    @require_image
    def add_center(self, source, event) -> None:
        new_color = self.active_color()
        if new_color == (0, 0, 0):
            return
        x, y = self.mouse_to_pixel(event.pos().x(), event.pos().y())
        if not self.channels.pixel_in_image((x, y)):
            return
        closest = self.centers.closest((x, y), radius=10)

        if closest is None:
            current_color = (0, 0, 0)
        else:
            current_color = self.centers[closest].color
            x, y = closest
        color = self.union_colors(current_color, new_color)
        self.centers[x, y] = Center(x, y, color, "")
        self.classify_center_by_regions((x, y), self.centers[x, y])
        self.label.update_image()

    def active_color(self) -> tuple[int, int, int]:
        channels = [k for k, v in self.colors.items() if v]
        result = (
            255 if 0 in channels else 0,
            255 if 1 in channels else 0,
            255 if 2 in channels else 0,
        )
        return result

    def union_colors(self, color1, color2) -> tuple[int, int, int]:
        return tuple(max(e1, e2) for e1, e2 in zip(color1, color2))

    def subtract_colors(self, color1, color2) -> tuple[int, int, int]:
        return tuple(max(0, e1 - e2) for e1, e2 in zip(color1, color2))

    @require_image
    def remove_center(self, source, event) -> None:
        x, y = self.mouse_to_pixel(event.pos().x(), event.pos().y())
        if not self.channels.pixel_in_image((x, y)):
            return
        closest = self.centers.closest((x, y), radius=30)
        if closest is not None:
            del self.centers[closest]
            self.label.update_image()

    @require_image
    def remove_region(self, source, event) -> None:
        x, y = self.mouse_to_pixel(event.pos().x(), event.pos().y())
        if not self.channels.pixel_in_image((x, y)):
            return
        for k, region in enumerate(self.regions):
            if region.contains_point((x, y), radius=30):
                self.regions.pop(k)
                self.classify_centers_by_regions()
                self.label.update_image()
                return

    def update_mouse_tooltip(self, source, event) -> None:
        if not self.has_img:
            return
        if not self.enable_tooltip:
            self.label.setToolTip("")
            return
        point = self.mouse_to_pixel(event.pos().x(), event.pos().y())
        if not self.channels.pixel_in_image(point):
            return

        buffer = []
        for region in self.regions:
            if region.contains(point):
                buffer.append(region.name)
        self.label.setToolTip(", ".join(buffer))
        self.label.setToolTipDuration(1500)

    def eventFilter(self, source, event) -> None:
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if (
                self.state == "setting_origin"
                and event.button() == QtCore.Qt.LeftButton
            ):
                self.set_origin(source, event)
            elif self.state == "modifying_centers":
                if event.button() == QtCore.Qt.LeftButton:
                    self.add_center(source, event)
                elif event.button() == QtCore.Qt.RightButton:
                    self.remove_center(source, event)
            elif self.state == "drawing_region":
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

    def keyPressEvent(self, event) -> None:
        modifiers = QApplication.keyboardModifiers()
        if event.key() == Qt.Key_R or event.key() == Qt.Key_1:
            self.mouse_colors[0].setChecked(not self.mouse_colors[0].isChecked())
        elif event.key() == Qt.Key_G or event.key() == Qt.Key_2:
            self.mouse_colors[1].setChecked(not self.mouse_colors[1].isChecked())
        elif event.key() == Qt.Key_B or event.key() == Qt.Key_3:
            self.mouse_colors[2].setChecked(not self.mouse_colors[2].isChecked())
        elif event.key() == Qt.Key_A:
            self.show_channels[0].setChecked(not self.show_channels[0].isChecked())
        elif event.key() == Qt.Key_S:
            if modifiers == Qt.ControlModifier:
                self.show_center_checkboxes[1].setChecked(
                    not self.show_center_checkboxes[1].isChecked()
                )
            else:
                self.show_channels[1].setChecked(not self.show_channels[1].isChecked())
        elif event.key() == Qt.Key_D:
            if modifiers == Qt.ControlModifier:
                self.show_center_checkboxes[2].setChecked(
                    not self.show_center_checkboxes[2].isChecked()
                )
            else:
                self.show_channels[2].setChecked(not self.show_channels[2].isChecked())
        elif event.key() == Qt.Key_F:
            if modifiers == Qt.ControlModifier:
                self.show_center_checkboxes[3].setChecked(
                    not self.show_center_checkboxes[3].isChecked()
                )
            else:
                self.show_channels[3].setChecked(not self.show_channels[3].isChecked())
        elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            if self.center_colors == "normal":
                self.center_colors = "black"
            else:
                self.center_colors = "normal"
            self.label.update_image()
        elif event.key() == Qt.Key_T:
            self.enable_tooltip = not self.enable_tooltip
        elif event.key() == Qt.Key_Question:
            print("*" * 20, "  Debug Information  ", "*" * 20)
            print("Centers:")
            for k, ((x, y), center) in enumerate(self.centers.items()):
                print(f"  Center {k}:")
                print("    Coordinates:", (x, y))
                print("    Color:", center.color)
                print("    Region:", center.region)
            print("*" * 20, "  End Debug Information  ", "*" * 20)
        event.accept()

    @require_image
    def set_origin(self, source, event: QtGui.QMouseEvent) -> None:
        x, y = self.mouse_to_pixel(event.pos().x(), event.pos().y())
        if not self.channels.pixel_in_image((x, y)):
            return
        self.origin = (x, y)
        self.state = "none"
        self.update_state_buttons()
        self.label.update_image()

    @require_image
    def mouse_to_pixel(self, x, y) -> tuple[int, int]:
        # Prefer NumPy C-style coordinates: x=row, y=column
        x, y = y, x
        x_pct = x / self.label.label.pixmap().width()
        y_pct = y / self.label.label.pixmap().height()
        result = int(x_pct * self.channels.width), int(y_pct * self.channels.height)
        return result

    # TODO: Type Overload
    @require_image
    def visible_channels(self) -> list[int]:
        result = [
            k for k, checkbox in enumerate(self.show_channels) if checkbox.isChecked()
        ]
        return result

    @require_image
    def write_csv(self) -> None:
        assert self.filename is not None
        if self.origin is None:
            error_msg("Must set origin to write CSV file.")
            return
        if len(self.centers) == 0:
            error_msg("Must set at least one center to write CSV file.")
            return

        x0, y0 = self.origin
        data = []
        data.append(["origin", x0, y0, 0, 0, 0, 0])
        for (x, y), center in self.centers.items():
            distance = np.sqrt((x - x0) * (x - x0) + (y - y0) * (y - y0))
            data.append(["center", x, y, distance, *center.color, center.region])
        for region in self.regions:
            for point in region.points:
                data.append(["region", *point, -1, 255, 69, 0, region.name])
        suggested_filename = f"{os.path.splitext(self.filename)[0]}.csv"
        name = CsvNameDialog.getSaveFileName(self, suggested_filename)

        pd.DataFrame(
            data,
            columns=["kind", "x", "y", "distance", "red", "green", "blue", "region"],
        ).to_csv(name, index=False)


def except_hook(cls, exception, tb) -> None:
    timestamp = datetime.datetime.now()
    stacktrace = traceback.format_tb(tb)
    msg = f"Error: {cls} -- {exception}\nStacktrace\n"
    for line in stacktrace:
        msg += f"{line}\n"
    filename = f"cob_error_{timestamp}.log"
    with open(filename, "w") as f:
        f.write(msg)
    error_msg(
        f"Unexpected exception occurred. The file \n\n{filename}\n\n was created with "
        f"the following log\n\n{msg}\n"
    )


if __name__ == "__main__":
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
