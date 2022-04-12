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
import itertools as it
from scipy.sparse import csr_matrix


def get_center(idx):
    x, y = idx[0].start + (idx[0].stop - idx[0].start) / 2, idx[1].start + (idx[1].stop - idx[1].start) / 2
    return int(x), int(y)


def get_surrounding(data, point, radius):
    x_low = point[0] - radius
    x_high = point[0] + radius
    y_low = point[1] - radius
    y_high = point[1] + radius
    return data[x_low:x_high, y_low:y_high]


def identify_centers(
        data,
        sigma: float = 1.0,
        gaussian_cutoff: int = 20,
        open_iterations: int = 2,
        open_structure=None,
        blob_size_min: int = 20,
        blob_size_max: int = 2000,
) -> list[tuple[float, float]]:
    smoothed = ndimage.gaussian_filter(data, sigma=sigma)
    binary_img = smoothed > gaussian_cutoff
    # plt.figure(figsize = (15, 10)); plt.imshow(binary_img); plt.show()

    # open_img = ndimage.binary_opening(binary_img, structure=open_structure, iterations=open_iterations)
    open_img = ndimage.binary_erosion(binary_img, structure=open_structure, iterations=open_iterations)
    # close_img = ndimage.binary_closing(open_img, iterations=close_iterations)
    close_img = open_img.copy()

    label_im, nb_labels = ndimage.label(close_img)

    labels = []
    for k, idx in enumerate(ndimage.find_objects(label_im, nb_labels), 1):
        subimg = label_im[idx]
        count = subimg[subimg == k].shape[0]
        if blob_size_min <= count <= blob_size_max:
            labels.append(k)
    large_blobs = np.isin(label_im, labels)
    label_im2, nb_labels2 = ndimage.label(large_blobs)

    centers = []
    for idx in ndimage.find_objects(label_im2, nb_labels2):
        center = get_center(idx)
        if get_surrounding(close_img, center, radius=5).mean() > 0.8:
            centers.append(center)

    return centers
def highlight_points(data, points, color):
    for point in points:
        highlight_point(data, point, color)


def highlight_points_dict(data, centers):
    for (x, y), center in centers.items():
        highlight_point(data, (x, y), center.color)


def highlight_line_segments(data, points, color):
    for (x1, y1), (x2, y2) in it.pairwise(points):
        draw_line(data, x1, y1, x2, y2, color)


def draw_line(mat, x0, y0, x1, y1, color):
    if not (0 <= x0 < mat.shape[0] and 0 <= x1 < mat.shape[0] and
            0 <= y0 < mat.shape[1] and 0 <= y1 < mat.shape[1]):
        raise ValueError('Invalid coordinates.')
    if (x0, y0) == (x1, y1):
        mat[x0, y0] = color
        return
    # Swap axes if Y slope is smaller than X slope
    transpose = abs(x1 - x0) < abs(y1 - y0)
    if transpose:
        # mat = mat.T
        mat = np.transpose(mat, (1, 0, 2))
        x0, y0, x1, y1 = y0, x0, y1, x1

    # Swap line direction to go left-to-right if necessary
    if x0 > x1:
        x0, y0, x1, y1 = x1, y1, x0, y0

    # Write line ends
    mat[x0, y0] = color
    mat[x1, y1] = color

    # Compute intermediate coordinates using line equation
    x = np.arange(x0 + 1, x1)
    y = np.round(((y1 - y0) / (x1 - x0)) * (x - x0) + y0).astype(x.dtype)

    # Write intermediate coordinates
    mat[x, y] = color


def highlight_point(data, point, color=(255, 255, 255)):
    xx, yy = point
    for k in range(5):
        for l in range(5):
            data[xx + k, yy + l] = color
            data[xx + k, yy - l] = color
            data[xx - k, yy + l] = color
            data[xx - k, yy - l] = color
            data[xx + l, yy + k] = color
            data[xx - l, yy + k] = color
            data[xx + l, yy - k] = color
            data[xx - l, yy - k] = color

    color = 255, 255, 255
    for k in range(7):
        for l in range(7):
            if k < 5 and l < 5:
                continue
            data[xx + k, yy + l] = color
            data[xx + k, yy - l] = color
            data[xx - k, yy + l] = color
            data[xx - k, yy - l] = color
            data[xx + l, yy + k] = color
            data[xx - l, yy + k] = color
            data[xx + l, yy - k] = color
            data[xx - l, yy - k] = color
