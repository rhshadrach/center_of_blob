__version__ = open('VERSION', "rt").read().strip()

from center_of_blob import analyze, centers, channels, main, main_image, popups

__all__ = ["analyze", "centers", "channels", "main", "main_image", "popups"]
