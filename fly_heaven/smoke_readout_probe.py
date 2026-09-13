"""Check whether Lana-driven neural activity reaches MN9."""

from pathlib import Path
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

MEMORY = Path(
    "outputs/fly-heaven/lana_cigarette_conditioning.npz"
)

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

print()
print("=== SELF-SMOKE MOTOR READOUT PROBE ===")
print("MN9 neurons:", len(mn9))
print("MN9 IDs:", reference.ids[mn9].tolist())


with np.load(MEMORY) as a:
    learned_weights = a["learned_weights"]


def run(label, learned=False):

    brain = MemoryBrain(
        GRAPH,
        circuit=circuit,
        eta=0.0,
    )

    if learned:
        brain.weight[circuit["edges"]] = learned_weights
        brain.weights_frozen = True

    song = VideoGamesStimulus(brain)

    darkness = np.zeros(
        len(brain.retina),
        dtype=np.float32,
    )

    total = 0
    events = []

    for local in range(TRIAL_BINS):

        counts, _ = brain.step(
            darkness,
            duration_ms=BIN_MS,
            learning=False,
            stimulation=song.stimulation(
                START_BIN + local
            ),
            lamina_bias=0.0,
        )

        n = int(counts[mn9].sum())

        if n:
            total += n
            events.append(
                (
                    round(local * BIN_MS / 1000, 3),
                    n,
                )
            )

    print()
    print(label)
    print(" MN9 spikes:", total)
    print(" smoke-choice events:", len(events))
    print(" event times:", events[:30])

    return total


pre = run("UNTRAINED", learned=False)
post = run("TRAINED", learned=True)

print()
print("=== RESULT ===")
print("MN9:", pre, "->", post)
