"""Convert MN9 activity under Lana into self-initiated SMOKE actions."""

import numpy as np
import pyarrow.feather as feather

from doom.engine import Brain
from doom_learning.common import GRAPH, ROOT
from doom_learning_v6.brain import MemoryBrain

from fly_heaven.audio_stimulus import VideoGamesStimulus
from fly_heaven.circuit import identify
from fly_heaven.smoke_action import SmokeDecoder


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

decoder = SmokeDecoder(
    action_duration_s=1.0
)

smoke_times = []
mn9_total = 0


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

    spikes = int(
        counts[mn9].sum()
    )

    mn9_total += spikes

    time_s = local * BIN_MS / 1000.0

    if decoder.update(
        time_s=time_s,
        mn9_spikes=spikes,
    ):
        smoke_times.append(
            round(time_s, 3)
        )


print()
print("=== SELF-INITIATED SMOKE ACTIONS ===")
print("MN9 spikes:", mn9_total)
print("SMOKE actions:", decoder.total_smokes)
print("SMOKE times:", smoke_times)
