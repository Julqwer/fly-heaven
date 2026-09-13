"""Does Lana specifically increase MN9 activity versus silence?"""

import numpy as np
import pyarrow.feather as feather

from doom.engine import Brain
from doom_learning.common import GRAPH, ROOT
from doom_learning_v6.brain import MemoryBrain

from fly_heaven.audio_stimulus import VideoGamesStimulus
from fly_heaven.circuit import identify


START_BIN = 16604
TRIAL_BINS = 500
BIN_MS = 10.0


reference = Brain(GRAPH)
circuit = identify(reference)

neurons = feather.read_table(
    ROOT / "connectome_data/malecns_v1/normalized/neurons.feather"
).to_pandas().set_index("source_id")

types = (
    neurons.loc[reference.ids, "cell_type"]
    .astype(str)
    .to_numpy()
)

mn9 = np.flatnonzero(types == "MN9").astype(np.int32)


def run(condition):

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

    total = 0
    active_bins = 0

    for local in range(TRIAL_BINS):

        if condition == "lana":
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

        n = int(counts[mn9].sum())

        total += n

        if n:
            active_bins += 1

    return total, active_bins


print()
print("=== MN9: SILENCE vs LANA ===")
print()

silence_spikes, silence_bins = run("silence")
lana_spikes, lana_bins = run("lana")

print("SILENCE")
print(" MN9 spikes:", silence_spikes)
print(" active 10-ms bins:", silence_bins)

print()
print("LANA")
print(" MN9 spikes:", lana_spikes)
print(" active 10-ms bins:", lana_bins)

print()
print("=== DIFFERENCE ===")
print("spikes:", silence_spikes, "->", lana_spikes)
