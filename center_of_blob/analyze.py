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
from scipy.sparse import csr_matrix


def identify_centers(data, sigma: float = 1.0) -> list[tuple[float, float]]:
    # first = imageio.imread('center_of_blob/first.jpg')

    level = 5
    sigma = 0.25
    blob_size = 50

    mask = (data[:, :, 0] > level) & (data[:, :, 1] > level) & (data[:, :, 2] > level)
    white_only = data.copy()
    white_only[:, :, 0] = white_only[:, :, 0] * mask
    white_only[:, :, 1] = white_only[:, :, 1] * mask
    white_only[:, :, 2] = white_only[:, :, 2] * mask

    gray = color.rgb2gray(white_only)

    # smoothed = ndimage.gaussian_filter(gray, sigma=sigma)
    # smoothed = gray
    # hist, bin_edges = np.histogram(smoothed, bins=60)
    # bin_centers = 0.5*(bin_edges[:-1] + bin_edges[1:])
    # binary_img = smoothed > 0.1

    # open_img = ndimage.binary_opening(binary_img, iterations=2)
    # open_img = binary_img
    # close_img = ndimage.binary_closing(open_img, iterations=2)

    result = gray > 0.04
    for k in range(10):
        result = ndimage.binary_opening(result, iterations=1)
        result = ndimage.binary_closing(result, iterations=1)

    label_im, nb_labels = ndimage.label(result)

    (unique, counts) = np.unique(label_im, return_counts=True)
    freq = np.asarray((unique, counts)).T

    labels = [e for e in freq[freq[:, 1] > blob_size][:, 0].tolist() if e != 0]
    large_blobs = np.isin(label_im, labels)
    label_im2, nb_labels2 = ndimage.label(large_blobs)

    centers = []

    def compute_M(data):
        cols = np.arange(data.size)
        return csr_matrix((cols, (data.ravel(), cols)),
                          shape=(data.max() + 1, data.size))

    def get_indices_sparse(data):
        M = compute_M(data)
        return [np.unravel_index(row.data, data.shape) for row in M]

    d = get_indices_sparse(label_im2)

    # TODO: Need better way to skip black; k == 0 below
    for k in range(1, len(d)):
        centers.append((int(d[k][0].mean()), int(d[k][1].mean())))

    return centers


def highlight_points(data, centers):
    result = data.copy()
    for center in centers:
        highlight_point(result, center)
    return result


def highlight_point(data, point, color=(255, 255, 255)):
    xx, yy = point
    for k in range(2):
        for l in range(2):
            data[xx + k, yy + l] = color
            data[xx + k, yy - l] = color
            data[xx - k, yy + l] = color
            data[xx - k, yy - l] = color
            data[xx + l, yy + k] = color
            data[xx - l, yy + k] = color
            data[xx + l, yy - k] = color
            data[xx - l, yy - k] = color