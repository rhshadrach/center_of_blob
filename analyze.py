import numpy as np
import pandas as pd
from scipy import misc
import imageio
import matplotlib.pyplot as plt
from scipy import ndimage
from skimage import color
from skimage import color, img_as_float
import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt
import matplotlib


def identify_centers(data, sigma: float = 1.0) -> list[tuple[float, float]]:
    mask = (data[:, :, 0] > 150) & (data[:, :, 1] < 100) & (data[:, :, 2] < 110)
    red_only = data.copy()
    red_only[:, :, 0] = red_only[:, :, 0] * mask
    red_only[:, :, 1] = red_only[:, :, 1] * mask
    red_only[:, :, 2] = red_only[:, :, 2] * mask

    gray = color.rgb2gray(red_only)

    smoothed = ndimage.gaussian_filter(gray, sigma=sigma)
    binary_img = smoothed > 0.1

    open_img = ndimage.binary_opening(binary_img, iterations=2)
    close_img = ndimage.binary_closing(open_img, iterations=2)

    label_im, nb_labels = ndimage.label(close_img)

    labels = []
    for k in range(1, nb_labels + 1):
        if label_im[label_im == k].shape[0] > 250:
            labels.append(k)
    large_blobs = np.isin(label_im, labels)
    label_im2, nb_labels2 = ndimage.label(large_blobs)

    centers = []
    for k in range(nb_labels2):
        center = tuple(np.argwhere(label_im2 == k).mean(axis=0).astype(int))
        centers.append(center)

    return centers


def highlight_points(data, centers):
    result = data.copy()
    for center in centers:
        highlight_point(result, center)
    return result


def highlight_point(data, point, color=(255, 255, 255)):
    xx, yy = point
    for k in range(10):
        for l in range(10):
            data[xx + k, yy + l] = color
            data[xx + k, yy - l] = color
            data[xx - k, yy + l] = color
            data[xx - k, yy - l] = color
            data[xx + l, yy + k] = color
            data[xx - l, yy + k] = color
            data[xx + l, yy - k] = color
            data[xx - l, yy - k] = color