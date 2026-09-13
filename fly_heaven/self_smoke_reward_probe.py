"""Closed-loop FLY HEAVEN probe.

Lana -> neural activity -> MN9 -> self-initiated SMOKE
-> 200 ms PAM07 appetitive reward -> plasticity.
"""

import numpy as np
import vizdoom as vzd

from doom.engine import Brain
from doom_learning.common import GRAPH
from doom_learning_v6.brain import MemoryBrain

from fly_heaven.audio_stimulus import VideoGamesStimulus
from fly_heaven.circuit import identify
from fly_heaven.reward import CIGARETTE_REWARD_CURRENT
from fly_heaven.smoke_action import SmokeDecoder


START_BIN = 16604
TRIAL_BINS = 500
BIN_MS = 10.0

REWARD_DURATION_S = 0.200

MN9_IDS = np.array(
    [10331, 16949],
    dtype=np.int64,
)


reference = Brain(GRAPH)
circuit = identify(reference)

brain = MemoryBrain(
    GRAPH,
    circuit=circuit,
    eta=0.001,
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

initial_weights = (
    brain.weight[circuit["edges"]].copy()
)

reward_until_s = -1.0
reward_events = 0


game = vzd.DoomGame()
game.load_config(
    "fly_heaven/scenarios/sunset_room.cfg"
)

game.set_available_buttons([
    vzd.Button.ATTACK
])

game.set_window_visible(True)
game.init()
game.new_episode()


print()
print("=== SELF-SMOKE + REWARD CLOSED LOOP ===")
print("No smoking timer.")
print("MN9 chooses SMOKE.")
print("Each SMOKE gives 200 ms PAM07 reward.")
print("Plasticity ON.")
print()


for local in range(TRIAL_BINS):

    t = local * BIN_MS / 1000.0

    stimulation = song.stimulation(
        START_BIN + local
    )

    # Reward continues for 200 ms after a self-initiated smoke.
    reward_on = t < reward_until_s

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
        stimulation=stimulation,
        lamina_bias=0.0,
    )

    mn9_spikes = int(
        counts[mn9].sum()
    )

    smoke = decoder.update(
        time_s=t,
        mn9_spikes=mn9_spikes,
    )

    if smoke:
        reward_events += 1
        reward_until_s = t + REWARD_DURATION_S

        print(
            f"{t:5.2f} s | MN9 -> SMOKE -> PAM07 REWARD"
        )

        game.make_action([1])

    else:
        game.make_action([0])


final_weights = (
    brain.weight[circuit["edges"]].copy()
)

efficacy = (
    final_weights / initial_weights
)


print()
print("=== CLOSED-LOOP RESULT ===")
print(
    "Self-initiated smokes:",
    decoder.total_smokes,
)
print(
    "Reward events:",
    reward_events,
)
print(
    "Mean KC->MBON05 efficacy:",
    round(float(efficacy.mean()), 6),
)
print(
    "Mean synaptic change:",
    f"{(efficacy.mean() - 1.0) * 100:+.2f}%",
)

input("Press Enter to close...")
game.close()
