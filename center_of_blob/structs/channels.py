from __future__ import annotations

from typing import Iterable, Literal

import numpy as np
from PIL import Image
from PIL.TiffImagePlugin import TiffImageFile

ChannelT = int | Literal["base", "r", "g", "b"]
N_CHANNELS = 4


class Channels:
    def __init__(self) -> None:
        # TODO: Can this depend on the file?
        self._mapper = {"base": 0, "r": 1, "g": 2, "b": 3}
        self.filename: str | None = None
        self.img: Image.Image | None = None
        self.arr: np.ndarray | None = None

        self.brightness = [(0, 255), (0, 255), (0, 255), (0, 255)]

        self._channels: list[np.ndarray] = []
        self._channel_cache: dict[int, np.ndarray] = {}

    def load_image(self, filename: str) -> bool:
        """Return is whether to disable channel 0"""
        img = Image.open(filename)
        assert isinstance(img, TiffImageFile)
        arr = np.asarray(img)

        channels = []
        if img.n_frames == 3:
            img.seek(0)
            channels.append(np.asarray(img))
            img.seek(0)
            green = np.asarray(img)
            img.seek(1)
            blue = np.asarray(img)
            img.seek(2)
            red = np.asarray(img)
            channels = [red, red, green, blue]
            result = True
        else:
            img.seek(0)
            channels.append(np.asarray(img))
            img.seek(1)
            channels.append(np.asarray(img))
            img.seek(2)
            channels.append(np.asarray(img))
            img.seek(3)
            channels.append(np.asarray(img))
            result = False

        # Only modify state upon success
        self.filename = filename
        self.img = img
        self.arr = arr
        self._channels = channels
        self._channel_cache = {}

        return result

    def set_brightness(self, channel: ChannelT, low: int, high: int) -> None:
        channel = self._funnel_channel(channel)
        if self.brightness[channel] != (low, high):
            self.brightness[channel] = (low, high)
            self.invalidate_channel_cache(channel)

    # TODO: Learn numpy type-hints
    @property
    def base(self) -> np.ndarray:
        return self._channels[0]

    # TODO: Learn numpy type-hints
    @property
    def r(self) -> np.ndarray:
        return self._channels[1]

    # TODO: Learn numpy type-hints
    @property
    def g(self) -> np.ndarray:
        return self._channels[2]

    # TODO: Learn numpy type-hints
    @property
    def b(self) -> np.ndarray:
        return self._channels[3]

    # TODO: Learn numpy type-hints
    def __getitem__(self, item: int) -> np.ndarray:
        return self._channels[item]

    def __len__(self) -> int:
        return len(self._channels)

    def invalidate_channel_cache(self, channel: int | None) -> None:
        if channel is None:
            self._channel_cache = {}
        elif channel in self._channel_cache:
            del self._channel_cache[channel]

    def _make_channel_data(self, channel: int) -> np.ndarray:
        if channel in self._channel_cache:
            return self._channel_cache[channel]
        low, high = self.brightness[channel]
        data = self._channels[channel]
        if low > 0 or high < 255:
            data = self.clip_data(data, low, high)
        filler = np.zeros_like(data, dtype="uint8")
        # TODO: Do we need to cast here?
        data = data.astype("uint8")
        if channel != 0:
            buffer = [filler if k != channel else data for k in range(1, 4)]
        else:
            buffer = 3 * [data]
        result = np.dstack(buffer)
        self._channel_cache[channel] = result
        return result

    # TODO: Learn numpy type-hints
    def as_rgb(self, channels: Iterable[ChannelT]) -> np.ndarray:
        channels = sorted(self._funnel_channel(channel) for channel in channels)
        result = sum(
            (self._make_channel_data(c) for c in range(0, 4) if c in channels),
            start=np.zeros((*self._channels[0].shape, 3), dtype="uint8"),
        )
        return result

    def clip_data(self, data: np.ndarray, low: float, high: float) -> np.ndarray:
        data = data.copy()
        off = data < low
        on = data > high
        data = np.rint(255.0 * (data - low) / (high - low)).astype(int)
        data[off] = 0
        data[on] = 255
        return data

    @property
    def mapper(self) -> dict[str, int]:
        return self._mapper.copy()

    @property
    def width(self) -> int:
        return self._channels[0].shape[1]

    @property
    def height(self) -> int:
        return self._channels[0].shape[0]

    def pixel_in_image(self, pixel: tuple[int, int]) -> bool:
        return (
            pixel[0] >= 0
            and pixel[0] < self.height
            and pixel[1] >= 0
            and pixel[1] < self.width
        )

    def _funnel_channel(self, channel: ChannelT) -> int:
        if isinstance(channel, str):
            result = self._mapper[channel]
        else:
            result = channel
        return result

    def color(self, channels: Iterable[ChannelT]) -> tuple[int, int, int]:
        channels = [self._funnel_channel(channel) for channel in channels]
        if channels == [0]:
            return (255, 255, 255)

        result = (
            255 if 1 in channels else 0,
            255 if 2 in channels else 0,
            255 if 3 in channels else 0,
        )
        return result
