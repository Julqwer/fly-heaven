"""Audio-derived Johnston's organ stimulation for FLY HEAVEN.

Real audio is transformed into two engineered mechanosensory proxies:
    JO-B: 20-100 Hz
    JO-A: 100-1000 Hz

The gain is an engineering calibration for this LIF model.
It is NOT a physical sound-pressure or antennal-displacement unit.
"""

from pathlib import Path

import numpy as np

from doom_learning.common import annotations


AUDIO_GAIN = 14.0
BIN_MS = 10.0

DATA = (
    Path(__file__).resolve().parent
    / "private_audio"
    / "video_games_jo.npz"
)


def identify_jo(brain):
    a = annotations(brain.ids)
    types = a.type.fillna("")

    jo_a = np.flatnonzero(
        types.str.startswith("JO-A")
    ).astype(np.int32)

    jo_b = np.flatnonzero(
        types.str.startswith("JO-B")
    ).astype(np.int32)

    if len(jo_a) != 50:
        raise ValueError(
            f"Expected 50 JO-A neurons, found {len(jo_a)}"
        )

    if len(jo_b) != 88:
        raise ValueError(
            f"Expected 88 JO-B neurons, found {len(jo_b)}"
        )

    return jo_a, jo_b


class VideoGamesStimulus:
    def __init__(self, brain):
        data = np.load(DATA)

        self.jo_a_signal = data["jo_a"]
        self.jo_b_signal = data["jo_b"]

        self.jo_a, self.jo_b = identify_jo(brain)

        if len(self.jo_a_signal) != len(self.jo_b_signal):
            raise ValueError("JO audio channels differ in length")

    @property
    def bins(self):
        return len(self.jo_a_signal)

    @property
    def duration_s(self):
        return self.bins * BIN_MS / 1000.0

    def stimulation(self, bin_index):
        if not 0 <= bin_index < self.bins:
            raise IndexError("Audio bin outside song")

        current_a = float(
            self.jo_a_signal[bin_index] * AUDIO_GAIN
        )

        current_b = float(
            self.jo_b_signal[bin_index] * AUDIO_GAIN
        )

        return [
            (self.jo_a, current_a),
            (self.jo_b, current_b),
        ]
