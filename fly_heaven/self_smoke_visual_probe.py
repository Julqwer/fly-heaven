"""MN9 directly triggers the visible SMOKE action. No timer, no reward yet."""

import numpy as np
import vizdoom as vzd

from doom.engine import Brain
from doom_learning.common import GRAPH
from doom_learning_v6.brain import MemoryBrain

from fly_heaven.audio_stimulus import VideoGamesStimulus
from fly_heaven.circuit import identify
from fly_heaven.smoke_action import SmokeDecoder


START_BIN = 16604
TRIAL_BINS = 500
BIN_MS = 10.0

MN9_IDS = np.array([10331, 16949], dtype=np.int64)


reference = Brain(GRAPH)
circuit = identify(reference)

brain = MemoryBrain(
    GRAPH,
    circuit=circuit,
    eta=0.0,
)

mn9 = np.flatnonzero(
    np.isin(brain.ids, MN9_IDS)
).astype(np.int32)

song = VideoGamesStimulus(brain)

darkness = np.zeros(
    len(brain.retina),
    dtype=np.float32,
)

decoder = SmokeDecoder(
    action_duration_s=1.0
)


game = vzd.DoomGame()
game.load_config(
    "fly_heaven/scenarios/sunset_room.cfg"
)

# ATTACK is only an internal actuator signal:
# MN9 -> ATTACK channel -> fly Pain state -> smoking animation.
game.set_available_buttons([
    vzd.Button.ATTACK
])

game.set_window_visible(True)
game.init()
game.new_episode()


print()
print("=== BRAIN-CONTROLLED SMOKE VISUAL PROBE ===")
print("No timer. No reward.")
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

    mn9_spikes = int(
        counts[mn9].sum()
    )

    t = local * BIN_MS / 1000.0

    smoke = decoder.update(
        time_s=t,
        mn9_spikes=mn9_spikes,
    )

    if smoke:
        print(
            f"MN9 -> SMOKE at {t:.2f} s"
        )

        game.make_action([1])
    else:
        game.make_action([0])


print()
print(
    "Self-initiated SMOKE actions:",
    decoder.total_smokes,
)

input("Press Enter to close...")
game.close()
