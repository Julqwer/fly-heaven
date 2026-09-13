"""Neural decoder for the self-initiated SMOKE action."""

class SmokeDecoder:
    def __init__(self, action_duration_s=1.0):
        self.action_duration_s = float(action_duration_s)
        self.busy_until_s = -1.0
        self.total_smokes = 0

    def update(self, time_s, mn9_spikes):
        """Return True only when MN9 initiates a new smoking action."""

        if time_s < self.busy_until_s:
            return False

        if mn9_spikes <= 0:
            return False

        self.total_smokes += 1
        self.busy_until_s = time_s + self.action_duration_s

        return True
