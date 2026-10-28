# Center of Blob

Center of Blob is a desktop app for marking the centers of blobs, such as cell
bodies, in multichannel microscopy images. For each blob you click, it records
which color channels the blob appears in, which user-drawn region it lies in,
and its distance from an origin you choose. The results are saved as a CSV
file that can be loaded again later to continue or check the work.

## Installation

Center of Blob needs Python 3.10 or newer. Install it from GitHub:

```bash
pip install git+https://github.com/rhshadrach/center_of_blob.git
```

Then start the app with:

```bash
python -m center_of_blob.main
```

To open an image as soon as the app starts, set `COB_IMAGE_PATH`:

```bash
COB_IMAGE_PATH=path/to/image.tif python -m center_of_blob.main
```

For real data to try the app on, see [Examples](#examples). The files are in the
repository's `examples/` folder, which `pip install` doesn't download.

A Windows executable is built by the "Build EXE" GitHub Actions workflow;
download the `cob-exe` artifact from a run on `main`.

## Usage

### Images

Click **Select Image File** to open a TIFF image. Two layouts are supported:

- **4 frames:** a base image followed by the red, green and blue channels.
- **3 frames:** the green, blue and red channels, in that order. These have no
  base image, so channel 0 is disabled.

### Marking centers

1. Click **Start setting origin**, then click the point to measure distances
   from.
2. Click **Start modifying centers**.
3. Tick the **Color Channel** checkboxes (1 = red, 2 = green, 3 = blue) for
   the channels the next blob appears in.
4. Left-click a blob to mark its center. Clicking within 10 pixels of an
   existing center adds the ticked channels to that center instead of
   creating a new one.
5. Right-click to remove the nearest center within 30 pixels.
6. Click **Stop modifying centers** when done.

### Regions

1. Click **Start drawing region** and click the corners of the region.
2. Click **Stop drawing region** and enter a name. Every region needs a name,
   and no two regions can share one; pressing Cancel discards the region.

Each center is assigned to the region it lies in. Where regions overlap, the
one drawn first wins. To remove a region, right-click within 30 pixels of one
of its corners while no mode is active.

### Saving and loading

Click **Write CSV** to save the origin, centers and regions; an origin and at
least one center are required. Click **Select Centers File** to load a saved
CSV onto the current image. Files with centers outside the image, no origin,
or regions without a unique, non-empty name are refused, and the current work
is kept.

### Viewing

- The **Channel** checkboxes in the first column show or hide each image
  channel. The sliders at the end of each row set that channel's brightness
  range.
- The **Channel** checkboxes in the second column show or hide the centers
  marked in each color.
- The top slider zooms from 100% to 800%; Ctrl+scroll also zooms.
- The second slider sets the size of the drawn centers.
- Hovering over the image shows the names of the regions under the mouse.

### Keyboard shortcuts

| Key                    | Action                                      |
| ---------------------- | ------------------------------------------- |
| R or 1, G or 2, B or 3 | Tick or untick a color channel for marking  |
| A                      | Show or hide channel 0                      |
| S, D, F                | Show or hide the red, green or blue channel |
| Ctrl+S, Ctrl+D, Ctrl+F | Show or hide the red, green or blue centers |
| Enter                  | Draw all centers in black, or back in color |
| T                      | Turn the region tooltip on or off           |
| ?                      | Print the centers to the console            |

The **Help** menu lists these shortcuts as well.

## CSV format

Each row has the columns `kind,x,y,distance,red,green,blue,region`:

- `kind` is `origin`, `center` or `region`.
- `x` and `y` are the pixel's row and column.
- `distance` is the center's distance from the origin, in pixels. It's 0 for
  the origin and -1 for region rows.
- `red`, `green` and `blue` are 255 for each channel a center appears in.
- `region` is the name of the region a center lies in (empty if none), or the
  region a corner belongs to. Each region's corners are listed in order,
  ending with the first corner again.

## Examples

`examples/` contains a 3-frame confocal image labeled Pax2-NeuN-Sall3, and the
centers file marked on it: 1,485 centers in three regions (Dorsal,
Intermediate and Ventral). Open the image with **Select Image File**, then the
CSV with **Select Centers File**.

## Development

```bash
git clone https://github.com/rhshadrach/center_of_blob.git
cd center_of_blob
uv sync
uv run prek install
uv run pytest tests
```
