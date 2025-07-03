import importlib.resources as pkg_resources

__version__ = pkg_resources.read_text("center_of_blob", "VERSION").strip()

from center_of_blob.widgets import popups, RangeSlider
from center_of_blob.structs import Center, Centers, Region

__all__ = [
    "popups",
    "Center",
    "Centers",
    "RangeSlider",
    "Region",
]
