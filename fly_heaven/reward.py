"""FLY HEAVEN appetitive reinforcement definition.

The cigarette is a visual/thematic wrapper for an engineered appetitive
unconditioned stimulus. This does not model nicotine pharmacology or
subjective pleasure.

Candidate reward circuit:
    PAM07 -> MBON05

Calibration:
    200 ms direct PAM07 stimulation
    +7.75 mV-equivalent current
    -> 4 spikes per PAM07 cell in the current model (~20 Hz during pulse)
"""

CIGARETTE_REWARD_CURRENT = 7.75
CIGARETTE_REWARD_DURATION_MS = 200.0

REWARD_DAN_TYPE = "PAM07"
REWARD_MBON_TYPE = "MBON05"
