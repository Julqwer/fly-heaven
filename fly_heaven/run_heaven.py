"""FLY HEAVEN persistent world.

Runs the sunset room indefinitely and loops the full local song.
Close with Ctrl+C.
"""

import subprocess
import time
from pathlib import Path

import vizdoom as vzd


SONG = Path(
    "fly_heaven/private_audio/"
    "video_games_mono.wav"
)


game = vzd.DoomGame()
game.load_config(
    "fly_heaven/scenarios/sunset_room.cfg"
)

game.set_window_visible(True)
game.init()
game.new_episode()

audio = None

print()
print("=== FLY HEAVEN ===")
print("Room: persistent")
print("Music: Video Games — loop")
print("Ctrl+C to stop")
print()


try:
    while True:

        # Restart song whenever it finishes.
        if audio is None or audio.poll() is not None:
            audio = subprocess.Popen(
                ["afplay", str(SONG)]
            )

        if game.is_episode_finished():
            game.new_episode()

        game.advance_action()

        # ViZDoom normally runs at 35 tics/s.
        time.sleep(1 / 35)

except KeyboardInterrupt:
    print()
    print("Closing FLY HEAVEN...")

finally:
    if audio is not None and audio.poll() is None:
        audio.terminate()

    game.close()
