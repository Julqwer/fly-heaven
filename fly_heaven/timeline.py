"""Shared timing for the FLY HEAVEN demo scene."""

START_BIN = 16604          # active Video Games excerpt
BIN_MS = 10

TRIAL_BINS = 500           # 5.0 s total scene
REWARD_BINS = 20           # 200 ms reward at the end

SMOKING_FRAMES = 16        # our overlay animation frames


def reward_on(local_bin: int) -> bool:
    return TRIAL_BINS - REWARD_BINS <= local_bin < TRIAL_BINS


def audio_bin(local_bin: int) -> int:
    if not 0 <= local_bin < TRIAL_BINS:
        raise IndexError(local_bin)
    return START_BIN + local_bin


def smoking_active(local_bin: int) -> bool:
    # show smoking gesture near the reward window
    return TRIAL_BINS - 40 <= local_bin < TRIAL_BINS + 10


def smoking_frame(local_bin: int) -> int:
    # map the active window onto our 16-frame animation loop
    phase = local_bin - (TRIAL_BINS - 40)
    if phase < 0:
        return 0
    return min(int(phase * SMOKING_FRAMES / 50), SMOKING_FRAMES - 1)


if __name__ == "__main__":
    print("Trial bins:", TRIAL_BINS)
    print("Reward bins:", REWARD_BINS)
    print("Reward starts at bin:", TRIAL_BINS - REWARD_BINS)
    print("Audio starts from source bin:", START_BIN)
