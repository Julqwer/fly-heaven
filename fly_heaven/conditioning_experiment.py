"""FLY HEAVEN main conditioning experiment.

Five independent-state conditioning trials:
    Video Games -> PAM07 appetitive reward during final 200 ms.

Synaptic weights are carried from trial to trial,
but neural activity is reset by creating a fresh brain each trial.

Then the learned weights are placed into a fresh brain
and Lana alone is compared with an untrained fresh brain.
"""

from pathlib import Path
import numpy as np

from doom.engine import Brain
from doom_learning.common import GRAPH
from doom_learning_v6.brain import MemoryBrain

from fly_heaven.audio_stimulus import VideoGamesStimulus
from fly_heaven.circuit import identify
from fly_heaven.reward import CIGARETTE_REWARD_CURRENT


START_BIN = 16604
TRIAL_BINS = 500
BIN_MS = 10.0
REWARD_BINS = 20

N_TRAINING_TRIALS = 5
ETA = 0.001


reference = Brain(GRAPH)
circuit = identify(reference)

edges = circuit["edges"]
plastic_kc = np.unique(circuit["pre"])

template = MemoryBrain(
    GRAPH,
    circuit=circuit,
    eta=0.0,
)

initial_weights = template.weight[edges].copy()


def fresh_brain(eta, weights=None):
    brain = MemoryBrain(
        GRAPH,
        circuit=circuit,
        eta=eta,
    )

    if weights is not None:
        brain.weight[edges] = weights
        # Probe must use exactly these supplied synaptic weights.
        # Otherwise MemoryBrain.step() reconstructs weights from
        # its zero memory_w state and silently restores baseline.
        brain.weights_frozen = True

    return brain


def probe(weights):
    """Lana alone on a fresh neural state."""
    brain = fresh_brain(
        eta=0.0,
        weights=weights,
    )

    song = VideoGamesStimulus(brain)

    darkness = np.zeros(
        len(brain.retina),
        dtype=np.float32,
    )

    mbon = 0
    pam = 0
    kc = 0

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

        mbon += int(
            counts[circuit["mb"]].sum()
        )

        pam += int(
            counts[circuit["dan"]].sum()
        )

        kc += int(
            counts[plastic_kc].sum()
        )

    return {
        "mbon": mbon,
        "pam": pam,
        "kc": kc,
    }


print()
print("=== FLY HEAVEN CONDITIONING EXPERIMENT ===")
print()
print("PRE-TEST: Lana alone on untrained brain...")

pre = probe(initial_weights)

print(" MBON05 spikes:", pre["mbon"])
print(" PAM07 spikes:", pre["pam"])
print(" plastic-KC spikes:", pre["kc"])


current_weights = initial_weights.copy()

print()
print(
    f"TRAINING: {N_TRAINING_TRIALS} x "
    "Lana + cigarette reward"
)
print()

# One learning brain for the whole conditioning session.
# Between trials we reset neural activity/traces but preserve
# the learned synaptic-memory state.
brain = fresh_brain(eta=ETA)
song = VideoGamesStimulus(brain)

darkness = np.zeros(
    len(brain.retina),
    dtype=np.float32,
)

for trial in range(1, N_TRAINING_TRIALS + 1):

    if trial > 1:
        brain.reset(keep_memory=True)

    for local in range(TRIAL_BINS):
        stimulation = song.stimulation(
            START_BIN + local
        )

        if local >= TRIAL_BINS - REWARD_BINS:
            stimulation.append(
                (
                    circuit["dan"],
                    CIGARETTE_REWARD_CURRENT,
                )
            )

        brain.step(
            darkness,
            duration_ms=BIN_MS,
            learning=True,
            stimulation=stimulation,
            lamina_bias=0.0,
        )

    current_weights = (
        brain.weight[edges].copy()
    )

    efficacy = (
        current_weights
        / initial_weights
    )

    print(
        f" trial {trial}: "
        f"mean efficacy={efficacy.mean():.6f} "
        f"| min={efficacy.min():.6f} "
        f"| max={efficacy.max():.6f}"
    )


print()
print("POST-TEST: Lana alone on trained fresh brain...")

post = probe(current_weights)

print(" MBON05 spikes:", post["mbon"])
print(" PAM07 spikes:", post["pam"])
print(" plastic-KC spikes:", post["kc"])


efficacy = (
    current_weights
    / initial_weights
)

print()
print("=== LEARNING SUMMARY ===")

print(
    "Mean KC->MBON05 efficacy:",
    round(float(efficacy.mean()), 6),
)

print(
    "Mean weight change:",
    f"{(efficacy.mean() - 1.0) * 100:+.2f}%",
)

print(
    "MBON05 response:",
    pre["mbon"],
    "->",
    post["mbon"],
    "spikes",
)

if pre["mbon"] > 0:
    change = (
        (post["mbon"] - pre["mbon"])
        / pre["mbon"]
        * 100.0
    )

    print(
        "MBON05 response change:",
        f"{change:+.1f}%",
    )


out = Path(
    "outputs/fly-heaven"
)

out.mkdir(
    parents=True,
    exist_ok=True,
)

np.savez_compressed(
    out / "lana_cigarette_conditioning.npz",
    edges=edges,
    initial_weights=initial_weights,
    learned_weights=current_weights,
    efficacy=efficacy,
)

print()
print(
    "Saved learned synapses to:",
    out / "lana_cigarette_conditioning.npz",
)
