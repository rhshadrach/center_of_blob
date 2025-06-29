import importlib.resources as pkg_resources

__version__ = pkg_resources.read_text("center_of_blob", "VERSION").strip()

from center_of_blob import analyze, centers, channels, main, main_image, popups
from center_of_blob.region import Region

__all__ = ["analyze", "centers", "channels", "main", "main_image", "popups", "Region"]
