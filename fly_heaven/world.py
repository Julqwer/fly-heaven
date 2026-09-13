"""FLY HEAVEN world boundary.

ViZDoom is used only as the renderer and movement engine.
The environment itself is a custom FLY HEAVEN scenario.
"""

from pathlib import Path

import vizdoom as vzd


class FlyHeavenWorld:
    def __init__(self, seed=41027):
        root = Path(__file__).resolve().parent
        scenarios = root / "scenarios"

        self.game = vzd.DoomGame()

        self.game.load_config(
            str(scenarios / "sunset_room.cfg")
        )

        self.game.set_doom_scenario_path(
            str((scenarios / "sunset_room.wad").resolve())
        )

        self.game.set_doom_game_path(
            str(Path(vzd.__file__).parent / "freedoom2.wad")
        )

        self.game.set_window_visible(False)
        self.game.set_sound_enabled(False)

        self.game.set_screen_format(vzd.ScreenFormat.RGB24)
        self.game.set_screen_resolution(
            vzd.ScreenResolution.RES_640X480
        )

        # The fly can turn and move.
        # No shooting. No combat controls.
        self.game.set_available_buttons(
            [
                vzd.Button.TURN_LEFT_RIGHT_DELTA,
                vzd.Button.MOVE_FORWARD_BACKWARD_DELTA,
            ]
        )

        self.game.set_button_max_value(
            vzd.Button.TURN_LEFT_RIGHT_DELTA, 6
        )
        self.game.set_button_max_value(
            vzd.Button.MOVE_FORWARD_BACKWARD_DELTA, 20
        )

        self.game.set_seed(seed)
        self.game.init()

        self.episode = 0
        self.tick = 0

        self.new_episode()

    def new_episode(self):
        self.game.new_episode()
        self.episode += 1
        self.tick = 0

    def pixels(self):
        state = self.game.get_state()

        if state is None:
            raise RuntimeError("FLY HEAVEN episode finished")

        return state.screen_buffer.copy()

    def act(self, turn=0.0, forward=0.0):
        reward = self.game.make_action(
            [float(turn), float(forward)],
            1,
        )

        self.tick += 1
        return float(reward)

    def close(self):
        self.game.close()
