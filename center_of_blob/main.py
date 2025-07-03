from __future__ import annotations

import datetime
import os
import sys
import traceback
from types import TracebackType
from typing import TypeVar, ParamSpec, Callable, Concatenate
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
from center_of_blob.structs import Center, Centers, Channels, N_CHANNELS, Region
from center_of_blob.widgets import popups


C = TypeVar("C", bound="MainWindow")
P = ParamSpec("P")
R = TypeVar("R")


def require_image(
    func: Callable[Concatenate[C, P], R],
) -> Callable[Concatenate[C, P], R | None]:
    """Decorator for methods that require the image."""

    def wrapper(self: C, *args: P.args, **kwargs: P.kwargs) -> R | None:
        if not self.has_img:
            popups.error_msg("Must load image first.")
            return None
        return func(self, *args, **kwargs)

    return wrapper


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.state = "none"
        self.origin: tuple[int, int] | None = None
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
        self.modify_centers_button = widgets.create_modify_centers(self)
        self.draw_region_button = widgets.create_draw_region(self)
        self.write_csv_button = widgets.create_write_csv_button(self)
        self.mouse_channel_checkboxes = widgets.create_mouse_channel_checkboxes(
            self, N_CHANNELS
        )
        self.show_channels = widgets.create_show_channels(self, N_CHANNELS)
        self.show_center_checkboxes = widgets.create_show_center_checkboxes(
            self, N_CHANNELS
        )
        self.brightness = widgets.create_brightness(self, N_CHANNELS)
        self.panel = widgets.create_panel(self)
        self.zoom_slider = widgets.create_zoom_slider(self)
        self.center_size_slider = widgets.create_center_size_slider(self)

        self.button_states["setting_origin"] = self.set_origin_button
        self.button_states["modifying_centers"] = self.modify_centers_button
        self.button_states["drawing_region"] = self.draw_region_button

        main = QWidget(self)
        self.setCentralWidget(main)
        layout = QGridLayout()
        layout.addWidget(self.img_path_button, 0, 0)
        layout.addWidget(self.centers_path_button, 0, 1)
        layout.addWidget(self.write_csv_button, 0, 2)
        layout.addWidget(self.set_origin_button, 1, 0)
        layout.addWidget(self.modify_centers_button, 1, 1)
        layout.addWidget(self.draw_region_button, 1, 2)
        for k in range(N_CHANNELS):
            layout.addWidget(self.show_channels[k], k, 3)
            if k > 0:
                layout.addWidget(self.show_center_checkboxes[k], k, 4)
            layout.addWidget(self.brightness[k], k, 5)
        for k, checkbox in enumerate(self.mouse_channel_checkboxes):
            layout.addWidget(checkbox, 3, k)
        layout.addWidget(self.zoom_slider, 4, 0, 1, 6)
        layout.addWidget(self.center_size_slider, 5, 0, 1, 6)
        layout.addWidget(self.panel, 6, 0, 1, 6)
        main.setLayout(layout)

        self.setWindowTitle("Center of Blob - No File Loaded")
        self.panel.label.installEventFilter(self)

        self.setGeometry(100, 100, 500, 400)

        menubar = self.menuBar()
        help = menubar.addMenu("Help")

        show_info = QAction("Info", self)
        show_info.setObjectName("action_show_info")
        show_info.triggered.connect(lambda: popups.info_dialog(self))
        help.addAction(show_info)

        show_shortcuts = QAction("Shortcuts", self)
        show_shortcuts.setObjectName("action_show_shortcuts")
        show_shortcuts.triggered.connect(lambda: popups.shortcuts_dialog(self))
        help.addAction(show_shortcuts)

        show_about = QAction("About", self)
        show_about.setObjectName("action_show_about")
        show_about.triggered.connect(popups.about_dialog)
        help.addAction(show_about)

        self.showMaximized()

        # Load image from environment variable for quick development iterations.
        img_path = os.environ.get("COB_IMAGE_PATH")
        if img_path is not None:
            self.get_img_file(img_path)

    @require_image
    def update_zoom(self) -> None:
        self.panel.zoom(self.zoom_slider.value() / 100)

    @require_image
    def update_center_size(self) -> None:
        self.panel.invalidate_cache()
        self.panel.update_image()

    def update_channels(self) -> None:
        self.panel.invalidate_cache()
        self.panel.update_image()

    def update_brightness(self) -> None:
        for channel, slider in enumerate(self.brightness):
            low = slider.low()
            high = slider.high()
            self.channels.set_brightness(channel, low, high)
        if self.has_img:
            self.panel.invalidate_cache()
            self.panel.update_image()

    def update_mouse_colors(self) -> None:
        for k, checkbox in enumerate(self.mouse_channel_checkboxes):
            self.colors[k] = checkbox.isChecked()

    def get_img_file(self, path: str | Path | None = None) -> None:
        if isinstance(path, str):
            path = Path(path)
        mypath = str(Path(__file__).resolve())
        if path is None:
            path = Path(popups.get_image_filename(self, directory=mypath)).resolve()
        try:
            # TODO: load_image resets channel state.. bad design
            disable_channel_0 = self.channels.load_image(str(path))
        except Exception as err:
            popups.error_msg(
                f"Failed to load file\n\n{path}\n\nError message:\n\n{err}"
            )
        else:
            # TODO: Move to a method, call from __init__
            self.state = "none"
            self.center_colors = "normal"
            self.show_centers = [1, 2, 3]
            self.has_img = True
            self.filename = str(path)
            self.setWindowTitle(f"Center of Blob - {path.parts[-1]}")
            self.centers.clear()
            self.origin = None
            self.panel.reset_image()
            if disable_channel_0:
                self.show_channels[0].setChecked(False)
                self.show_channels[0].setDisabled(True)
                self.brightness[0].setDisabled(True)
            else:
                self.show_channels[0].setDisabled(False)
                self.brightness[0].setDisabled(False)
            self.panel._cache = None
            self.current_region = None
            self.regions = []
            self.colors = {0: False, 1: False, 2: False}
            self.panel.update_image()

    def make_regions(self, data: pd.DataFrame) -> None:
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

        path = popups.get_centers_filename(main_window=self, directory=mypath)
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
            popups.error_msg(
                f"Failed to load file\n\n{path}\n\nError message:\n\n{err}"
            )
            return

        # TODO: Reset state better
        self.origin = None
        self.centers = new_centers
        self.colors = {0: False, 1: False, 2: False}
        self.show_centers = [1, 2, 3]
        self.center_colors = "normal"

        if not self.centers.are_in_img(self.channels[1].shape):
            self.centers.clear()
            popups.error_msg(
                "Centers file has points outside of image bounds. Refusing file."
            )
            return

        try:
            point = data[data["kind"] == "origin"].iloc[0]
            self.origin = point["x"], point["y"]
        except Exception as err:
            popups.error_msg(
                f"Failed to find origin in centers file. Error message:\n\n{err}"
            )
            self.centers.clear()
            return

        self.panel.update_image()

    @require_image
    def click_set_origin(self) -> None:
        if self.state == "setting_origin":
            self.state = "none"
        else:
            self.state = "setting_origin"
        self.update_state_buttons()

    @require_image
    def click_modify_centers(self) -> None:
        if self.state == "modifying_centers":
            self.state = "none"
        else:
            self.state = "modifying_centers"
        self.update_state_buttons()

    @require_image
    def click_draw_region(self) -> None:
        if self.state == "drawing_region":
            self.state = "none"
        else:
            self.state = "drawing_region"
            self.current_region = Region()
        self.update_state_buttons()

    def add_region_point(
        self, source: QtCore.QObject, event: QtGui.QMouseEvent
    ) -> None:
        assert self.current_region is not None
        x, y = self.mouse_to_pixel(event.pos().x(), event.pos().y())
        if not self.channels.pixel_in_image((x, y)):
            return
        self.current_region.add_point((x, y))
        self.panel.update_image()

    def classify_center_by_regions(
        self, point: tuple[int, int], center: Center
    ) -> None:
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
            popups.error_msg(msg)
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
            self.panel.update_image()
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
    def add_center(self, source: QtCore.QObject, event: QtGui.QMouseEvent) -> None:
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
        self.panel.update_image()

    def active_color(self) -> tuple[int, int, int]:
        channels = [k for k, v in self.colors.items() if v]
        result = (
            255 if 0 in channels else 0,
            255 if 1 in channels else 0,
            255 if 2 in channels else 0,
        )
        return result

    def union_colors(
        self, color1: tuple[int, int, int], color2: tuple[int, int, int]
    ) -> tuple[int, int, int]:
        result = (
            max(color1[0], color2[0]),
            max(color1[1], color2[1]),
            max(color1[2], color2[2]),
        )
        return result

    def subtract_colors(
        self, color1: tuple[int, int, int], color2: tuple[int, int, int]
    ) -> tuple[int, int, int]:
        result = (
            max(0, color1[0] - color2[0]),
            max(0, color1[1] - color2[1]),
            max(0, color1[2] - color2[2]),
        )
        return result

    @require_image
    def remove_center(self, source: QtCore.QObject, event: QtGui.QMouseEvent) -> None:
        x, y = self.mouse_to_pixel(event.pos().x(), event.pos().y())
        if not self.channels.pixel_in_image((x, y)):
            return
        closest = self.centers.closest((x, y), radius=30)
        if closest is not None:
            del self.centers[closest]
            self.panel.update_image()

    @require_image
    def remove_region(self, source: QtCore.QObject, event: QtGui.QMouseEvent) -> None:
        point = self.mouse_to_pixel(event.pos().x(), event.pos().y())
        if not self.channels.pixel_in_image(point):
            return

        distances = {}
        for k, region in enumerate(self.regions):
            distances[k] = region.distance_to_boundary_point(point)
        k = sorted(distances.items(), key=lambda item: item[1])[0][0]
        if self.regions[k].has_boundary_point(point, radius=30):
            self.regions.pop(k)
            self.classify_centers_by_regions()
            self.panel.update_image()
            return

    def update_mouse_tooltip(
        self, source: QtCore.QObject, event: QtGui.QMouseEvent
    ) -> None:
        if not self.has_img:
            return
        if not self.enable_tooltip:
            self.panel.setToolTip("")
            return
        point = self.mouse_to_pixel(event.pos().x(), event.pos().y())
        if not self.channels.pixel_in_image(point):
            return

        buffer = []
        for region in self.regions:
            if region.contains(point):
                buffer.append(region.name)
        self.panel.setToolTip(", ".join(buffer))
        self.panel.setToolTipDuration(1500)

    def eventFilter(self, source: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if (
            isinstance(event, QtGui.QMouseEvent)
            and event.type() == QtCore.QEvent.MouseButtonPress
        ):
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
        if (
            isinstance(event, QtGui.QMouseEvent)
            and event.type() == QtCore.QEvent.MouseMove
            and self.enable_tooltip
        ):
            self.update_mouse_tooltip(source, event)

        if isinstance(event, QtGui.QWheelEvent) and event.type() == QtCore.QEvent.Wheel:
            modifiers = QApplication.keyboardModifiers()
            if bool(modifiers == QtCore.Qt.ControlModifier):
                self.zoom_slider.setValue(
                    self.zoom_slider.value() + int(event.angleDelta().y() / 5)
                )
                event.ignore()
        return super().eventFilter(source, event)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        modifiers = QApplication.keyboardModifiers()
        if event.key() == Qt.Key_R or event.key() == Qt.Key_1:
            self.mouse_channel_checkboxes[0].setChecked(
                not self.mouse_channel_checkboxes[0].isChecked()
            )
        elif event.key() == Qt.Key_G or event.key() == Qt.Key_2:
            self.mouse_channel_checkboxes[1].setChecked(
                not self.mouse_channel_checkboxes[1].isChecked()
            )
        elif event.key() == Qt.Key_B or event.key() == Qt.Key_3:
            self.mouse_channel_checkboxes[2].setChecked(
                not self.mouse_channel_checkboxes[2].isChecked()
            )
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
            self.panel.update_image()
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
    def set_origin(self, source: QtCore.QObject, event: QtGui.QMouseEvent) -> None:
        x, y = self.mouse_to_pixel(event.pos().x(), event.pos().y())
        if not self.channels.pixel_in_image((x, y)):
            return
        self.origin = (x, y)
        self.state = "none"
        self.update_state_buttons()
        self.panel.update_image()

    def mouse_to_pixel(self, x: int, y: int) -> tuple[int, int]:
        # Prefer NumPy C-style coordinates: x=row, y=column
        x, y = y, x
        x_pct = x / self.panel.label.pixmap().width()
        y_pct = y / self.panel.label.pixmap().height()
        result = int(x_pct * self.channels.width), int(y_pct * self.channels.height)
        return result

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
            popups.error_msg("Must set origin to write CSV file.")
            return
        if len(self.centers) == 0:
            popups.error_msg("Must set at least one center to write CSV file.")
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
        name = popups.get_csv_save_filename(
            main_window=self, directory=suggested_filename
        )

        pd.DataFrame(
            data,
            columns=["kind", "x", "y", "distance", "red", "green", "blue", "region"],
        ).to_csv(name, index=False)


# TODO: Add test
def except_hook(
    cls: type[BaseException], exception: BaseException, tb: TracebackType | None
) -> None:
    timestamp = datetime.datetime.now()
    stacktrace = traceback.format_tb(tb)
    msg = f"Error: {cls} -- {exception}\nStacktrace\n"
    for line in stacktrace:
        msg += f"{line}\n"
    filename = f"cob_error_{timestamp}.log"
    with open(filename, "w") as f:
        f.write(msg)
    popups.error_msg(
        f"Unexpected exception occurred. The file \n\n{filename}\n\n was created with "
        f"the following log\n\n{msg}\n"
    )


if __name__ == "__main__":
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
