from typing import Literal, Iterable

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

    def load_image(self, filename: str):
        self.filename = filename
        self.img = Image.open(self.filename)
        self.arr = np.asarray(self.img)
        self._channels = []

        self.img.seek(0)
        self._channels.append(np.asarray(self.img))
        self.img.seek(1)
        self._channels.append(np.asarray(self.img))
        self.img.seek(2)
        self._channels.append(np.asarray(self.img))
        self.img.seek(3)
        self._channels.append(np.asarray(self.img))

    def set_brightness(self, channel, low, high):
        channel = self._funnel_channel(channel)
        self.brightness[channel] = (low, high)

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

    # TODO: Learn numpy type-hints
    def as_rgb(self, channels: Iterable[ChannelT]):
        channels = sorted(self._funnel_channel(channel) for channel in channels)
        filler = np.zeros_like(self._channels[0])
        result = None

        # Only gather color-specific channels if necessary
        if channels != [0]:
            # Channel 0 is handled specially below
            buffer = []
            for channel in range(1, len(self._channels)):
                if channel in channels:
                    low, high = self.brightness[channel]
                    data = self._channels[channel]
                    if low > 0 or high < 255:
                        data = self.clip_data(data, low, high)
                    buffer.append(data.astype('int'))
                else:
                    buffer.append(filler)
            result = np.dstack(buffer)

        if 0 in channels:
            data = self._channels[0]
            low, high = self.brightness[0]
            if low > 0 or high < 255:
                data = self.clip_data(data, low, high)
            channel0 = np.dstack(3*[data.astype('int')])
            if result is None:
                result = channel0
            else:
                result += channel0
                result = result.clip(max=255)
        result = result.astype('uint8')

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
