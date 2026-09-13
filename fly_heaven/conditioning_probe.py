"""FLY HEAVEN paired-stimulus wiring probe.

No learning occurs here.

Protocol:
    5 s active excerpt of Video Games
    +
    cigarette reward during the final 200 ms

Purpose:
    verify that the audio stimulus reaches Kenyon cells while PAM07
    reinforcement is present.

This is a pathway/integration test, not conditioning.
"""

import numpy as np

from doom.engine import Brain
from doom_learning.common import GRAPH
from doom_learning_v6.brain import MemoryBrain

from fly_heaven.audio_stimulus import VideoGamesStimulus
from fly_heaven.circuit import identify
from fly_heaven.reward import (
    CIGARETTE_REWARD_CURRENT,
    CIGARETTE_REWARD_DURATION_MS,
)


# Previously selected representative active window.
START_BIN = 16604

TRIAL_BINS = 500          # 5.00 s
BIN_MS = 10.0

REWARD_BINS = int(
    round(CIGARETTE_REWARD_DURATION_MS / BIN_MS)
)


reference = Brain(GRAPH)
circuit = identify(reference)

brain = MemoryBrain(
    GRAPH,
    circuit=circuit,
    eta=0.0,              # absolutely no plasticity in this probe
)

song = VideoGamesStimulus(brain)

darkness = np.zeros(
    len(brain.retina),
    dtype=np.float32,
)

# Only KCs that actually provide plastic inputs to MBON05.
plastic_kc = np.unique(circuit["pre"])


totals = {
    "jo_a": 0,
    "jo_b": 0,
    "plastic_kc": 0,
    "pam07": 0,
    "mbon05": 0,
}

active_plastic_kc = set()

reward_start = TRIAL_BINS - REWARD_BINS


for local_bin in range(TRIAL_BINS):
    song_bin = START_BIN + local_bin

    stimulation = song.stimulation(song_bin)

    reward_on = local_bin >= reward_start

    if reward_on:
        stimulation.append(
            (
                circuit["dan"],
                CIGARETTE_REWARD_CURRENT,
            )
        )

    counts, _ = brain.step(
        darkness,
        duration_ms=BIN_MS,
        learning=False,
        stimulation=stimulation,
        lamina_bias=0.0,
    )

    kc_counts = counts[plastic_kc]

    totals["jo_a"] += int(
        counts[song.jo_a].sum()
    )

    totals["jo_b"] += int(
        counts[song.jo_b].sum()
    )

    totals["plastic_kc"] += int(
        kc_counts.sum()
    )

    totals["pam07"] += int(
        counts[circuit["dan"]].sum()
    )

    totals["mbon05"] += int(
        counts[circuit["mb"]].sum()
    )

    fired = np.flatnonzero(kc_counts)

    active_plastic_kc.update(
        fired.tolist()
    )


print()
print("=== FLY HEAVEN PAIRED-STIMULUS PROBE ===")
print("Song excerpt: 166.04–171.04 s")
print(
    "Reward:",
    f"final {CIGARETTE_REWARD_DURATION_MS:.0f} ms",
    f"@ +{CIGARETTE_REWARD_CURRENT}",
)
print()

print(
    "JO-A spikes:",
    totals["jo_a"],
    f"| neurons={len(song.jo_a)}",
)

print(
    "JO-B spikes:",
    totals["jo_b"],
    f"| neurons={len(song.jo_b)}",
)

print()
print(
    "Plastic KC -> MBON05 population:",
    len(plastic_kc),
    "neurons",
)

print(
    "Active plastic KCs:",
    len(active_plastic_kc),
    "/",
    len(plastic_kc),
)

print(
    "Plastic-KC spikes:",
    totals["plastic_kc"],
)

print()
print(
    "PAM07 spikes:",
    totals["pam07"],
)

print(
    "MBON05 spikes:",
    totals["mbon05"],
)

print()
print("LEARNING: OFF")
