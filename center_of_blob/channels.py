from typing import Literal, Iterable

import numpy as np
from PIL import Image

ChannelT = int | Literal['base', 'r', 'g', 'b']
N_CHANNELS = 4


class Channels:
    def __init__(self, filename: str):
        # TODO: Can this depend on the file?
        self._mapper = {'base': 0, 'r': 1, 'g': 2, 'b': 3}
        self.filename = filename
        self.img = Image.open(self.filename)
        # TODO: Error checking: # of frames
        self.arr = np.asarray(self.img)

        self.brightness_add = N_CHANNELS * [0]
        self.brightness_mul = N_CHANNELS * [1]

        self._channels = []
        self.img.seek(0)
        self._channels.append(np.asarray(self.img))
        self.img.seek(1)
        self._channels.append(np.asarray(self.img))
        self.img.seek(2)
        self._channels.append(np.asarray(self.img))
        self.img.seek(3)
        self._channels.append(np.asarray(self.img))

        self._combined = self.as_rgb(range(len(self._channels)))

    def set_brightness_add(self, channel, value):
        channel = self._funnel_channel(channel)
        self.brightness_add[channel] = value

    def set_brightness_mul(self, channel, value):
        channel = self._funnel_channel(channel)
        self.brightness_mul[channel] = value

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
    @property
    def all(self):
        return self._combined

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
                    data = self._channels[channel] * self.brightness_mul[channel]
                    buffer.append(data.astype('uint8'))
                else:
                    buffer.append(filler)
            result = np.dstack(buffer)

        if 0 in channels:
            data = self._channels[0] * self.brightness_mul[0]
            channel0 = np.dstack(3*[data.astype('uint8')])
            if result is None:
                result = channel0
            else:
                result += channel0

        return result

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
            result = [channel]
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
