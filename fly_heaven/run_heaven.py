"""FLY HEAVEN — persistent closed-loop world.

Full Video Games loops indefinitely.

Closed loop:
audio -> JO -> full MaleCNS -> MN9 -> self-initiated SMOKE
-> visible smoking action -> PAM07 appetitive reward.

The first five self-initiated smoking rewards are plastic.
After that, learned weights are frozen, while the fly may continue
to choose SMOKE and receive reward indefinitely.

Ctrl+C to stop.
"""

import queue
import subprocess
import threading
import time
from pathlib import Path

import numpy as np
import vizdoom as vzd

from doom.engine import Brain
from doom_learning.common import GRAPH
from doom_learning_v6.brain import MemoryBrain

from fly_heaven.audio_stimulus import (
    BIN_MS,
    VideoGamesStimulus,
)
from fly_heaven.circuit import identify
from fly_heaven.reward import CIGARETTE_REWARD_CURRENT
from fly_heaven.smoke_action import SmokeDecoder


SONG_WAV = Path(
    "fly_heaven/private_audio/video_games_mono.wav"
)

OUTPUT = Path(
    "outputs/fly-heaven/heaven_session_latest.npz"
)

MN9_IDS = np.array(
    [10331, 16949],
    dtype=np.int64,
)

REWARD_STEPS = 20       # 20 x 10 ms = 200 ms
TRAINING_SMOKES = 5
ETA = 0.001

GAME_HZ = 35.0


# ------------------------------------------------------------
# Brain
# ------------------------------------------------------------

reference = Brain(GRAPH)
circuit = identify(reference)

brain = MemoryBrain(
    GRAPH,
    circuit=circuit,
    eta=ETA,
)

song = VideoGamesStimulus(brain)

mn9 = np.flatnonzero(
    np.isin(brain.ids, MN9_IDS)
).astype(np.int32)

if len(mn9) != 2:
    raise RuntimeError(
        f"Expected 2 MN9 neurons, found {len(mn9)}"
    )

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


# ------------------------------------------------------------
# Shared runtime state
# ------------------------------------------------------------

stop_event = threading.Event()

smoke_requests = queue.Queue()

audio_lock = threading.Lock()

audio_state = {
    "started_at": None,
    "loop": 0,
}

stats = {
    "smokes": 0,
    "rewards": 0,
    "training_smokes": 0,
}

weights_frozen = False


# ------------------------------------------------------------
# Audio
# ------------------------------------------------------------

def audio_loop():

    while not stop_event.is_set():

        with audio_lock:
            audio_state["started_at"] = time.monotonic()
            audio_state["loop"] += 1
            loop_number = audio_state["loop"]

        print(
            f"\n🎵 Video Games loop {loop_number}",
            flush=True,
        )

        audio = subprocess.Popen(
            ["afplay", str(SONG_WAV)]
        )

        while (
            audio.poll() is None
            and not stop_event.is_set()
        ):
            time.sleep(0.1)

        if stop_event.is_set():
            if audio.poll() is None:
                audio.terminate()
            break


def current_song_position():

    with audio_lock:
        started = audio_state["started_at"]
        loop_number = audio_state["loop"]

    if started is None:
        return None, None, None

    position_s = (
        time.monotonic() - started
    )

    position_s %= song.duration_s

    bin_index = int(
        position_s * 1000.0 / BIN_MS
    )

    bin_index = min(
        max(bin_index, 0),
        song.bins - 1,
    )

    return position_s, bin_index, loop_number


# ------------------------------------------------------------
# ViZDoom observer world
# ------------------------------------------------------------

def game_loop():

    game = vzd.DoomGame()

    game.load_config(
        "fly_heaven/scenarios/sunset_room.cfg"
    )

    # ATTACK is only our invisible actuator channel:
    # MN9 -> SMOKE request -> fly Pain state -> animation.
    game.set_available_buttons([
        vzd.Button.ATTACK
    ])

    game.set_window_visible(True)
    game.init()
    game.new_episode()

    try:

        while not stop_event.is_set():

            if game.is_episode_finished():
                game.new_episode()

            attack = 0

            try:
                smoke_requests.get_nowait()
                attack = 1
            except queue.Empty:
                pass

            game.make_action([attack])

            time.sleep(1.0 / GAME_HZ)

    except vzd.ViZDoomUnexpectedExitException:

        print(
            "\nViZDoom window closed.",
            flush=True,
        )

        stop_event.set()

    finally:

        try:
            game.close()
        except Exception:
            pass


# ------------------------------------------------------------
# Save learned state
# ------------------------------------------------------------

def save_session():

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    learned_weights = (
        brain.weight[circuit["edges"]].copy()
    )

    efficacy = (
        learned_weights / initial_weights
    )

    np.savez_compressed(
        OUTPUT,
        edges=circuit["edges"],
        initial_weights=initial_weights,
        learned_weights=learned_weights,
        efficacy=efficacy,
        smokes=np.array(
            [stats["smokes"]],
            dtype=np.int64,
        ),
        rewards=np.array(
            [stats["rewards"]],
            dtype=np.int64,
        ),
        training_smokes=np.array(
            [stats["training_smokes"]],
            dtype=np.int64,
        ),
    )

    return float(efficacy.mean())


# ------------------------------------------------------------
# Start world
# ------------------------------------------------------------

print()
print("===================================")
print("          FLY HEAVEN")
print("===================================")
print()
print("Music: Video Games — infinite loop")
print("Smoking: chosen by MN9")
print("Reward: PAM07, 200 ms per SMOKE")
print(
    f"Plasticity: first {TRAINING_SMOKES} "
    "self-initiated rewards"
)
print("After training: weights frozen")
print()
print("Ctrl+C to leave heaven.")
print()


audio_thread = threading.Thread(
    target=audio_loop,
    daemon=True,
)

game_thread = threading.Thread(
    target=game_loop,
    daemon=True,
)

audio_thread.start()
game_thread.start()


# Wait until audio has actually started.
while not stop_event.is_set():

    with audio_lock:
        ready = (
            audio_state["started_at"]
            is not None
        )

    if ready:
        break

    time.sleep(0.01)


# ------------------------------------------------------------
# Persistent neural closed loop
# ------------------------------------------------------------

try:

    while not stop_event.is_set():

        position_s, bin_index, loop_number = (
            current_song_position()
        )

        if bin_index is None:
            time.sleep(0.01)
            continue

        stimulation = song.stimulation(
            bin_index
        )

        counts, _ = brain.step(
            darkness,
            duration_ms=BIN_MS,
            learning=not weights_frozen,
            stimulation=stimulation,
            lamina_bias=0.0,
        )

        mn9_spikes = int(
            counts[mn9].sum()
        )

        wall_time = time.monotonic()

        smoke = decoder.update(
            time_s=wall_time,
            mn9_spikes=mn9_spikes,
        )

        if not smoke:
            continue

        # ----------------------------
        # MN9 independently chose SMOKE
        # ----------------------------

        stats["smokes"] += 1

        smoke_requests.put_nowait(True)

        training_this_smoke = (
            not weights_frozen
            and stats["training_smokes"]
            < TRAINING_SMOKES
        )

        if training_this_smoke:
            stats["training_smokes"] += 1

        phase = (
            "TRAINING"
            if training_this_smoke
            else "FROZEN"
        )

        print(
            f"🚬 SMOKE #{stats['smokes']} "
            f"| song {position_s:6.2f}s "
            f"| loop {loop_number} "
            f"| {phase}",
            flush=True,
        )

        # ----------------------------
        # Consequence of its own action:
        # 200 ms PAM07 reward.
        #
        # No new SMOKE decision is decoded
        # during this reward pulse.
        # ----------------------------

        for _ in range(REWARD_STEPS):

            reward_position, reward_bin, _ = (
                current_song_position()
            )

            if reward_bin is None:
                reward_bin = bin_index

            reward_stimulation = (
                song.stimulation(reward_bin)
            )

            reward_stimulation.append(
                (
                    circuit["dan"],
                    CIGARETTE_REWARD_CURRENT,
                )
            )

            brain.step(
                darkness,
                duration_ms=BIN_MS,
                learning=training_this_smoke,
                stimulation=reward_stimulation,
                lamina_bias=0.0,
            )

        stats["rewards"] += 1

        print(
            "   ↳ PAM07 reward",
            flush=True,
        )

        # Freeze only AFTER the fifth
        # complete rewarded smoking action.
        if (
            stats["training_smokes"]
            >= TRAINING_SMOKES
            and not weights_frozen
        ):

            brain.weights_frozen = True
            weights_frozen = True

            mean_efficacy = save_session()

            print()
            print(
                "🧠 TRAINING COMPLETE — "
                "synaptic weights frozen"
            )

            print(
                "   mean KC->MBON05 efficacy:",
                f"{mean_efficacy:.6f}",
            )

            print(
                "   fly may continue smoking "
                "and receiving reward"
            )

            print()


except KeyboardInterrupt:

    print()
    print("Leaving FLY HEAVEN...")


finally:

    stop_event.set()

    mean_efficacy = save_session()

    print()
    print("=== SESSION SUMMARY ===")
    print(
        "Self-initiated SMOKEs:",
        stats["smokes"],
    )
    print(
        "PAM07 rewards:",
        stats["rewards"],
    )
    print(
        "Training SMOKEs:",
        stats["training_smokes"],
    )
    print(
        "Final mean KC->MBON05 efficacy:",
        f"{mean_efficacy:.6f}",
    )
    print(
        "Saved:",
        OUTPUT,
    )
    print()

    time.sleep(0.2)
