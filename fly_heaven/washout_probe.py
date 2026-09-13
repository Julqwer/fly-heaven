"""Measure post-song activity decay with learning disabled."""

import numpy as np

from doom.engine import Brain
from doom_learning.common import GRAPH
from doom_learning_v6.brain import MemoryBrain

from fly_heaven.audio_stimulus import VideoGamesStimulus
from fly_heaven.circuit import identify


START_BIN = 16604
BIN_MS = 10.0

SONG_BINS = 500       # 5 s
WASHOUT_BINS = 1500   # 15 s


reference = Brain(GRAPH)
circuit = identify(reference)

brain = MemoryBrain(
    GRAPH,
    circuit=circuit,
    eta=0.0,
)

song = VideoGamesStimulus(brain)

darkness = np.zeros(
    len(brain.retina),
    dtype=np.float32,
)

plastic_kc = np.unique(circuit["pre"])

kc_per_second = []
pam_per_second = []

kc_acc = 0
pam_acc = 0


print()
print("=== FLY HEAVEN WASHOUT PROBE ===")
print("5 s song -> 15 s silence")
print("LEARNING OFF")
print()


for local in range(SONG_BINS + WASHOUT_BINS):

    if local < SONG_BINS:
        stimulation = song.stimulation(
            START_BIN + local
        )
    else:
        stimulation = None

    counts, _ = brain.step(
        darkness,
        duration_ms=BIN_MS,
        learning=False,
        stimulation=stimulation,
        lamina_bias=0.0,
    )

    if local >= SONG_BINS:
        kc_acc += int(
            counts[plastic_kc].sum()
        )

        pam_acc += int(
            counts[circuit["dan"]].sum()
        )

        washout_local = local - SONG_BINS

        if (washout_local + 1) % 100 == 0:
            second = (washout_local + 1) // 100

            kc_per_second.append(kc_acc)
            pam_per_second.append(pam_acc)

            print(
                f"silence {second:2d} s:"
                f" KC={kc_acc:6d}"
                f" | PAM07={pam_acc:4d}"
            )

            kc_acc = 0
            pam_acc = 0
