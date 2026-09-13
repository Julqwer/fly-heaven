"""First controlled FLY HEAVEN plasticity smoke test.

Three fresh, identical brains:
1. paired: Video Games + cigarette reward in final 200 ms
2. song_only: Video Games without reward
3. reward_only: silence + cigarette reward in final 200 ms

This is NOT yet evidence of learned preference.
It tests whether the candidate plasticity rule is associative enough
to distinguish paired stimulation from its components.
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


START_BIN = 16604
TRIAL_BINS = 500
BIN_MS = 10.0
REWARD_BINS = int(
    round(CIGARETTE_REWARD_DURATION_MS / BIN_MS)
)


reference = Brain(GRAPH)
circuit = identify(reference)


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

    for local in range(TRIAL_BINS):
        stimulation = []

        song_on = condition in (
            "paired",
            "song_only",
        )

        reward_on = (
            condition in ("paired", "reward_only")
            and local >= TRIAL_BINS - REWARD_BINS
        )

        if song_on:
            stimulation.extend(
                song.stimulation(START_BIN + local)
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
            counts[np.unique(circuit["pre"])].sum()
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
        "changed_0_1pct": int(
            np.count_nonzero(np.abs(delta) > 0.001)
        ),
        "depressed_0_1pct": int(
            np.count_nonzero(delta < -0.001)
        ),
        "potentiated_0_1pct": int(
            np.count_nonzero(delta > 0.001)
        ),
    }


print()
print("=== FLY HEAVEN PLASTICITY SMOKE TEST ===")
print("One 5 s trial per fresh brain.")
print()

for condition in [
    "paired",
    "song_only",
    "reward_only",
]:
    result = run(condition)

    print()
    print(condition.upper())
    print(" PAM07 spikes:", result["pam_spikes"])
    print(" plastic-KC spikes:", result["kc_spikes"])
    print(
        " mean efficacy:",
        round(result["mean_efficacy"], 6),
    )
    print(
        " min/max efficacy:",
        round(result["min_efficacy"], 6),
        "/",
        round(result["max_efficacy"], 6),
    )
    print(
        " >0.1% changed edges:",
        result["changed_0_1pct"],
        "/",
        len(circuit["edges"]),
    )
    print(
        " depressed:",
        result["depressed_0_1pct"],
        "| potentiated:",
        result["potentiated_0_1pct"],
    )
