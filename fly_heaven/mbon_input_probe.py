"""Measure Lana-driven KC -> MBON05 synaptic input before vs after conditioning.

Uses the SAME presynaptic KC spike train for both conditions so the
difference reflects learned KC->MBON05 weights, not different network states.
"""

from pathlib import Path
import numpy as np

from doom.engine import Brain
from doom_learning.common import GRAPH
from doom_learning_v6.brain import MemoryBrain

from fly_heaven.audio_stimulus import VideoGamesStimulus
from fly_heaven.circuit import identify


START_BIN = 16604
TRIAL_BINS = 500
BIN_MS = 10.0

MEMORY_FILE = Path(
    "outputs/fly-heaven/lana_cigarette_conditioning.npz"
)


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


with np.load(MEMORY_FILE) as data:
    initial_weights = data["initial_weights"]
    learned_weights = data["learned_weights"]


pre = circuit["pre"]
edges = circuit["edges"]

post = brain.post[edges]

kc_spikes_per_edge = np.zeros(
    len(edges),
    dtype=np.float64,
)


print()
print("=== MBON05 LANA INPUT PROBE ===")
print("Replaying Lana with learning OFF...")
print()


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

    kc_spikes_per_edge += counts[pre]


initial_drive = (
    kc_spikes_per_edge
    * initial_weights
)

learned_drive = (
    kc_spikes_per_edge
    * learned_weights
)


initial_total = float(initial_drive.sum())
learned_total = float(learned_drive.sum())

change_pct = (
    (learned_total - initial_total)
    / initial_total
    * 100.0
)


print(
    "Active KC->MBON05 edges:",
    int(np.count_nonzero(kc_spikes_per_edge)),
    "/",
    len(edges),
)

print()
print(
    "Initial weighted KC input:",
    round(initial_total, 3),
)

print(
    "Learned weighted KC input:",
    round(learned_total, 3),
)

print(
    "Lana-driven input change:",
    f"{change_pct:+.2f}%",
)


print()
print("Per MBON05 neuron:")

for mb in circuit["mb"]:

    mask = post == mb

    initial = float(
        initial_drive[mask].sum()
    )

    learned = float(
        learned_drive[mask].sum()
    )

    pct = (
        (learned - initial)
        / initial
        * 100.0
        if initial != 0
        else float("nan")
    )

    print(
        f" {brain.ids[mb]}:"
        f" {initial:.3f}"
        f" -> {learned:.3f}"
        f" ({pct:+.2f}%)"
    )


print()
print(
    "NOTE: this is a weighted presynaptic-spike proxy,"
)

print(
    "not a direct measurement of membrane current."
)
