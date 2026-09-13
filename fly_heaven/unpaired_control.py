"""Strict matched temporal-association control.

Both fresh brains receive:
- the same 5 s Video Games excerpt
- the same 200 ms PAM07 reward
- the same total duration: 8.2 s
- reward at exactly the same absolute time: 8.0-8.2 s

Only song timing differs.

PAIRED:
    silence 0.0-3.2 s
    song    3.2-8.2 s
    reward  8.0-8.2 s

UNPAIRED:
    song    0.0-5.0 s
    silence 5.0-8.0 s
    reward  8.0-8.2 s
"""

import numpy as np

from doom.engine import Brain
from doom_learning.common import GRAPH
from doom_learning_v6.brain import MemoryBrain

from fly_heaven.audio_stimulus import VideoGamesStimulus
from fly_heaven.circuit import identify
from fly_heaven.reward import CIGARETTE_REWARD_CURRENT


START_BIN = 16604
BIN_MS = 10.0

SONG_BINS = 500
PAIR_DELAY_BINS = 320

REWARD_START = 800
REWARD_BINS = 20

TOTAL_BINS = 820


reference = Brain(GRAPH)
circuit = identify(reference)

plastic_kc = np.unique(circuit["pre"])


def run(condition):
    brain = MemoryBrain(
        GRAPH,
        circuit=circuit,
        eta=0.001,
    )

    song = VideoGamesStimulus(brain)

    darkness = np.zeros(
        len(brain.retina),
        dtype=np.float32,
    )

    baseline = brain.baseline_plastic.copy()

    pam_spikes = 0
    kc_spikes = 0

    print(f"Running {condition}...", flush=True)

    for local in range(TOTAL_BINS):
        stimulation = []

        if condition == "paired":
            song_local = local - PAIR_DELAY_BINS
            song_on = 0 <= song_local < SONG_BINS

        elif condition == "unpaired":
            song_local = local
            song_on = 0 <= song_local < SONG_BINS

        else:
            raise ValueError(condition)

        if song_on:
            stimulation.extend(
                song.stimulation(
                    START_BIN + song_local
                )
            )

        reward_on = (
            REWARD_START
            <= local
            < REWARD_START + REWARD_BINS
        )

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
            learning=True,
            stimulation=stimulation or None,
            lamina_bias=0.0,
        )

        pam_spikes += int(
            counts[circuit["dan"]].sum()
        )

        kc_spikes += int(
            counts[plastic_kc].sum()
        )

    fraction = (
        brain.weight[circuit["edges"]]
        / baseline
    )

    delta = fraction - 1.0

    return {
        "pam_spikes": pam_spikes,
        "kc_spikes": kc_spikes,
        "mean_efficacy": float(fraction.mean()),
        "min_efficacy": float(fraction.min()),
        "max_efficacy": float(fraction.max()),
        "changed": int(
            np.count_nonzero(np.abs(delta) > 0.001)
        ),
        "depressed": int(
            np.count_nonzero(delta < -0.001)
        ),
        "potentiated": int(
            np.count_nonzero(delta > 0.001)
        ),
    }


print()
print("=== STRICT MATCHED PAIRED vs UNPAIRED ===")
print("Reward fixed at 8.0-8.2 s in both conditions.")
print()

results = {}

for condition in ["paired", "unpaired"]:
    results[condition] = run(condition)
    r = results[condition]

    print()
    print(condition.upper())
    print(" PAM07 spikes:", r["pam_spikes"])
    print(" plastic-KC spikes:", r["kc_spikes"])
    print(" mean efficacy:", round(r["mean_efficacy"], 6))
    print(
        " min/max efficacy:",
        round(r["min_efficacy"], 6),
        "/",
        round(r["max_efficacy"], 6),
    )
    print(
        " >0.1% changed:",
        r["changed"],
        "/",
        len(circuit["edges"]),
    )
    print(
        " depressed:",
        r["depressed"],
        "| potentiated:",
        r["potentiated"],
    )

print()
print("=== DIFFERENCE ===")
print(
    "paired - unpaired mean efficacy:",
    round(
        results["paired"]["mean_efficacy"]
        - results["unpaired"]["mean_efficacy"],
        6,
    ),
)
