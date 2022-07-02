from typing import Literal, Iterable, Optional

import numpy as np
from PIL import Image

ChannelT = int | Literal['base', 'r', 'g', 'b']
N_CHANNELS = 4


class Channels:
    def __init__(self):
        # TODO: Can this depend on the file?
        self._mapper = {'base': 0, 'r': 1, 'g': 2, 'b': 3}
        self.filename = None
        self.img = None
        self.arr = None

        self.brightness = [(0, 255), (0, 255), (0, 255), (0, 255)]

        self._channels = []
        self._channel_cache = {}

    def load_image(self, filename: str) -> bool:
        """Return is whether to disable channel 0"""
        self.filename = filename
        self.img = Image.open(self.filename)
        self.arr = np.asarray(self.img)
        self._channels = []

        if self.img.n_frames == 3:
            self.img.seek(0)
            self._channels.append(np.asarray(self.img))
            self.img.seek(0)
            self._channels.append(np.asarray(self.img))
            self.img.seek(1)
            self._channels.append(np.asarray(self.img))
            self.img.seek(2)
            self._channels.append(np.asarray(self.img))
            return True
        else:
            self.img.seek(0)
            self._channels.append(np.asarray(self.img))
            self.img.seek(1)
            self._channels.append(np.asarray(self.img))
            self.img.seek(2)
            self._channels.append(np.asarray(self.img))
            self.img.seek(3)
            self._channels.append(np.asarray(self.img))
            return False

    def set_brightness(self, channel, low, high):
        channel = self._funnel_channel(channel)
        if self.brightness[channel] != (low, high):
            self.brightness[channel] = (low, high)
            self.invalidate_channel_cache(channel)

    # TODO: Learn numpy type-hints
    @property
    def base(self):
        return self._channels[0]

    # TODO: Learn numpy type-hints
    @property
    def r(self):
        return self._channels[1]

    # TODO: Learn numpy type-hints
    @property
    def g(self):
        return self._channels[2]

    # TODO: Learn numpy type-hints
    @property
    def b(self):
        return self._channels[3]

    # TODO: Learn numpy type-hints
    def __getitem__(self, item: ChannelT):
        return self._channels[item]

    def __len__(self) -> int:
        return len(self._channels)

    def invalidate_channel_cache(self, channel: Optional[int]):
        if channel is None:
            self._channel_cache = {}
        else:
            del self._channel_cache[channel]

    def _make_channel_data(self, channel):
        if channel in self._channel_cache:
            return self._channel_cache[channel]
        low, high = self.brightness[channel]
        data = self._channels[channel]
        if low > 0 or high < 255:
            data = self.clip_data(data, low, high)
        filler = np.zeros_like(data, dtype='uint8')
        # TODO: Do we need to cast here?
        data = data.astype('uint8')
        if channel != 0:
            buffer = [filler if k != channel else data for k in range(1, 4)]
        else:
            buffer = 3 * [data]
        result = np.dstack(buffer)
        self._channel_cache[channel] = result
        return result

    # TODO: Learn numpy type-hints
    def as_rgb(self, channels: Iterable[ChannelT]):
        channels = sorted(self._funnel_channel(channel) for channel in channels)
        result = None

        if channels != [0]:
            result = sum(self._make_channel_data(c) for c in range(1, 4) if c in channels)
        if 0 in channels or len(channels) == 0:
            channel0 = self._make_channel_data(0)
            if result is None:
                result = channel0
            else:
                result += channel0
        return result

    def clip_data(self, data, low, high):
        data = data.copy()
        off = data < low
        on = data > high
        data = np.rint(255.0 * (data - low) / (high - low)).astype(int)
        data[off] = 0
        data[on] = 255
        return data

    @property
    def mapper(self):
        return self._mapper.copy()

    @property
    def width(self):
        return self._channels[0].shape[1]

    @property
    def height(self):
        return self._channels[0].shape[0]

    def _funnel_channel(self, channel: ChannelT) -> int:
        if isinstance(channel, str):
            result = self._mapper[channel]
        else:
            result = channel
        return result

    def color(self, channels):
        channels = [self._funnel_channel(channel) for channel in channels]
        if channels == [0]:
            return (255, 255, 255)

        buffer = [0, 0, 0]
        for channel in range(1, len(self._channels)):
            if channel not in channels:
                continue
            buffer[channel-1] = 255
        return tuple(buffer)
